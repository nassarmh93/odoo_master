# Part of Odoo. See LICENSE file for full copyright and licensing details.

import uuid

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from hashlib import sha256
from markupsafe import Markup
from random import randint
from werkzeug.urls import url_join, url_quote, url_encode

from odoo import _, api, fields, models, Command
from odoo.tools import consteq, email_normalize, formataddr, groupby, get_lang, is_html_empty
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import hmac


class SignRequestItem(models.Model):
    _name = 'sign.request.item'
    _description = "Signature Request Item"
    _inherit = ['portal.mixin']
    _rec_name = 'partner_id'

    def _default_access_token(self):
        return str(uuid.uuid4())

    def _get_mail_link(self, email, subject):
        return "mailto:%s?subject=%s" % (url_quote(email), url_quote(subject))

    # this display_name (with sudo) is used for many2many_tags especially the partner_id is private
    display_name = fields.Char(compute_sudo=True)

    partner_id = fields.Many2one('res.partner', string="Signer", ondelete='restrict')
    sign_request_id = fields.Many2one('sign.request', string="Signature Request", ondelete='cascade', required=True, copy=False)
    sign_item_value_ids = fields.One2many('sign.request.item.value', 'sign_request_item_id', string="Value")
    reference = fields.Char(related='sign_request_id.reference', string="Document Name")
    mail_sent_order = fields.Integer(default=1)
    communication_company_id = fields.Many2one(related='sign_request_id.communication_company_id')

    access_token = fields.Char(required=True, default=_default_access_token, readonly=True, copy=False, groups="base.group_system")
    access_via_link = fields.Boolean('Accessed Through Token', copy=False)
    role_id = fields.Many2one('sign.item.role', string="Role", required=True, readonly=True)
    sms_number = fields.Char(related='partner_id.phone', readonly=False, depends=(['partner_id']), store=True, copy=False)
    sms_token = fields.Char('SMS Token', readonly=True, copy=False)
    signed_without_extra_auth = fields.Boolean('Signed Without Extra Authentication', default=False, readonly=True, copy=False)

    signature = fields.Binary(attachment=True, copy=False)
    frame_hash = fields.Char(size=256, compute='_compute_frame_hash')
    signing_date = fields.Date('Signed on', readonly=True, copy=False)
    state = fields.Selection([
        ("sent", "To Sign"),
        ("completed", "Completed"),
        ("canceled", "Cancelled"),
    ], readonly=True, default="sent", copy=False, index=True)
    color = fields.Integer(compute='_compute_color')

    signer_email = fields.Char(string='Email', compute="_compute_email", store=True)
    is_mail_sent = fields.Boolean(readonly=True, copy=False, help="The signature mail has been sent.")
    change_authorized = fields.Boolean(related='role_id.change_authorized')

    latitude = fields.Float(digits=(10, 7), copy=False)
    longitude = fields.Float(digits=(10, 7), copy=False)

    @api.constrains('signer_email')
    def _check_signer_email_validity(self):
        if any(sri.partner_id and not sri.signer_email for sri in self):
            raise ValidationError(_("All signers must have valid email addresses"))

    @api.constrains('partner_id', 'role_id')
    def _check_signers_validity(self):
        # this check allows one signer to be False, which is used to "share" a sign template
        self.sign_request_id._check_signers_roles_validity()
        self.sign_request_id._check_signers_partners_validity()

    @api.depends('signer_email')
    def _compute_frame_hash(self):
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        for sri in self:
            if sri.partner_id:
                sri.frame_hash = sha256((sri.signer_email + db_uuid).encode()).hexdigest()
            else:
                sri.frame_hash = ''

    @api.depends('partner_id.name')
    def _compute_display_name(self):
        for sri in self:
            sri.display_name = sri.partner_id.display_name if sri.partner_id else _('Public User')

    def write(self, vals):
        if vals.get('partner_id') is False:
            raise UserError(_("You need to define a signatory"))
        request_items_reassigned = self.env['sign.request.item']
        if vals.get('partner_id'):
            request_items_reassigned |= self.filtered(lambda sri: sri.partner_id.id != vals['partner_id'])
            if any(sri.state != 'sent'
                   or sri.sign_request_id.state != 'sent'
                   or (sri.partner_id and not sri.role_id.change_authorized)
                   or sri.sign_request_id.state == 'shared'
                   for sri in request_items_reassigned):
                raise UserError(_("You cannot reassign this signatory"))
            new_sign_partner = self.env['res.partner'].browse(vals.get('partner_id'))
            for request_item in request_items_reassigned:
                sign_request = request_item.sign_request_id
                old_sign_user = request_item.partner_id.user_ids[:1]
                # remove old activities for internal users if they are no longer one of the unsigned signers of their sign requests
                if old_sign_user and old_sign_user.has_group('sign.group_sign_user') and \
                        not sign_request.request_item_ids.filtered(
                            lambda sri: sri.partner_id == request_item.partner_id and sri.state == 'sent' and sri not in request_items_reassigned):
                    sign_request.activity_unlink(['mail.mail_activity_data_todo'], user_id=old_sign_user.id)
                # create logs
                sign_request.message_post(
                    body=_('The contact of %(role)s has been changed from %(old_partner)s to %(new_partner)s.',
                           role=request_item.role_id.name, old_partner=request_item.partner_id.name, new_partner=new_sign_partner.name))

            # add new followers
            request_items_reassigned.sign_request_id.message_subscribe(partner_ids=[vals.get('partner_id')])
            # add new activities for internal users
            new_sign_user = self.env['res.users'].search([
                ('partner_id', '=', vals.get('partner_id')),
                ('all_group_ids', 'in', [self.env.ref('sign.group_sign_user').id])
            ], limit=1)
            if new_sign_user:
                activity_ids = set(request_items_reassigned.sign_request_id.activity_search(['mail.mail_activity_data_todo'], user_id=new_sign_user.id).mapped('res_id'))
                request_items_reassigned.sign_request_id.filtered(lambda sr: sr.id not in activity_ids)._schedule_activity(new_sign_user)

        res = super().write(vals)

        # change access token
        for request_item in request_items_reassigned.filtered(lambda sri: sri.is_mail_sent):
            request_item.sudo().update({'access_token': self._default_access_token()})
            request_item.is_mail_sent = False
        return res

    def _cancel(self, no_access=True):
        """ Cancel a SignRequestItem. It can only be used in the SignRequest.cancel or SignRequest._refuse
        :param bool no_access: Whether the sign request item cannot be accessed by the previous link in the email
        """
        for request_item in self:
            request_item.write({
                'state': 'canceled' if request_item.state == 'sent' else request_item.state,
                'signing_date': fields.Date.context_today(self) if request_item.state == 'sent' else request_item.signing_date,
                'is_mail_sent': False if no_access else request_item.is_mail_sent,
            })
            request_item.sudo().write({'access_token': self._default_access_token() if no_access else request_item.access_token})

    def _refuse(self, refusal_reason):
        self.ensure_one()
        if not self.env.su:
            raise UserError(_("This function can only be called with sudo."))
        if self.state != 'sent' or self.sign_request_id.state != 'sent':
            raise UserError(_("This sign request item cannot be refused"))
        self.env['sign.log'].create({'sign_request_item_id': self.id, 'action': 'refuse'})
        self.write({'signing_date': fields.Date.context_today(self), 'state': 'canceled'})
        refuse_user = self.partner_id.user_ids[:1]
        # mark the activity as done for the refuser
        if refuse_user and refuse_user.has_group('sign.group_sign_user'):
            self.sign_request_id.activity_feedback(['mail.mail_activity_data_todo'], user_id=refuse_user.id)
        refusal_reason = _("No specified reason") if not refusal_reason or refusal_reason.isspace() else refusal_reason
        message_post = _("The signature has been refused by %(partner)s(%(role)s)", partner=self.partner_id.name, role=self.role_id.name)
        message_post = Markup('{}<p style="white-space: pre">{}</p>').format(message_post, refusal_reason)
        self.sign_request_id.message_post(body=message_post)
        self.sign_request_id._refuse(self.partner_id, refusal_reason)

    def _get_url_parameters(self, signer, expiry_link_timestamp):
        return url_encode({
                'timestamp': expiry_link_timestamp,
                'exp': signer._generate_expiry_signature(signer.id, expiry_link_timestamp)
            })

    def _get_access_token(self, signer):
        return signer.sudo().access_token

    def _send_signature_access_mail(self):
        for signer in self:
            signer_email_normalized = email_normalize(signer.signer_email or '')
            signer_lang = get_lang(self.env, lang_code=signer.partner_id.lang).code
            context = {'lang': signer_lang}
            # We hide the validity information if it is the default (6 month from the create_date)
            has_default_validity = signer.sign_request_id.validity and signer.sign_request_id.validity - relativedelta(months=6) == signer.sign_request_id.create_date.date()
            expiry_link_timestamp = signer._generate_expiry_link_timestamp()
            url_params = self._get_url_parameters(signer, expiry_link_timestamp)
            partial_url = "sign/document/mail/%(request_id)s/%(access_token)s?%(url_params)s" % {
                    'request_id': signer.sign_request_id.id, 
                    'access_token': self._get_access_token(signer), 
                    'url_params': url_params
                }
            link_sign = url_join(signer.get_base_url(), partial_url)
            link_cancel = link_sign + '&refuseDocument=1'
            body = self.env['ir.qweb']._render('sign.sign_template_mail_request', {
                'record': signer,
                'link': link_sign,
                'link_cancel': link_cancel,
                'subject': signer.sign_request_id.subject,
                'body': signer.sign_request_id.message if not is_html_empty(signer.sign_request_id.message) else False,
                'use_sign_terms': self.env['ir.config_parameter'].sudo().get_param('sign.use_sign_terms'),
                'user_signature': signer.create_uid.signature,
                'show_validity': signer.sign_request_id.validity and not has_default_validity,
            }, lang=signer_lang, minimal_qcontext=True)

            attachment_ids = signer.sign_request_id.attachment_ids.ids
            self.env['sign.request']._message_send_mail(
                body, 'sign.sign_mail_notification_light',
                {'record_name': signer.sign_request_id.reference},
                {'model_description': _('Signature'),
                 'company': signer.communication_company_id or signer.sign_request_id.create_uid.company_id,
                 'partner': signer.partner_id},
                {'email_from': signer.create_uid.email_formatted,
                 'author_id': signer.create_uid.partner_id.id,
                 'email_to': formataddr((signer.partner_id.name, signer_email_normalized)),
                 'attachment_ids': attachment_ids,
                 'subject': signer.sign_request_id.subject},
                force_send=self.env.context.get('force_send', True),  # only force_send if not from cron
                lang=signer_lang,
            )
            signer.is_mail_sent = True
            del context

    def _edit_and_sign(self, signature, **kwargs):
        """ Sign sign request items at once.
        :param signature: dictionary containing signature values and corresponding ids
        :param dict new_sign_items: {id (str): values (dict)}
            id: negative: negative random itemId(sync_id) in pdfviewer (the sign item is new created in the pdfviewer and should be created)
            values: values to create
        """
        self.ensure_one()
        if not self.env.su:
            raise UserError(_("This function can only be called with sudo."))
        elif self.state != 'sent' or self.sign_request_id.state != 'sent':
            raise UserError(_("This sign request item cannot be signed"))
        elif self.sign_request_id.validity and self.sign_request_id.validity < fields.Date.today():
            raise UserError(_('This sign request is not valid anymore'))

        # edit request template while signing
        new_sign_items = kwargs.get('new_sign_items', False)
        if new_sign_items:
            if any(int(item_id) >= 0 for item_id in new_sign_items):
                raise UserError(_("Existing sign items are not allowed to be changed"))
            if any(item['responsible_id'] != self.role_id.id for item in new_sign_items.values()):
                raise UserError(_("You can only add new items for the current role"))
            sign_request = self.sign_request_id
            if sign_request.nb_closed != 0:
                raise UserError(_("The document has been signed by a signer and cannot be edited"))
            # copy the old template
            old_template = sign_request.template_id
            new_template = old_template.copy({
                'favorited_ids': [Command.link(sign_request.create_uid.id), Command.link(self.env.user.id)],
                'active': False,
                'sign_item_ids': []
            }).sudo(False)
            existing_item_id_map = old_template._copy_sign_items_to(new_template)

            # edit the new template(add new sign items)
            new_item_id_map = new_template.update_from_pdfviewer(new_sign_items)
            sign_request.template_id = new_template
            item_id_map = dict(existing_item_id_map, **new_item_id_map)

            # update the item ids in signature
            new_signature = {}
            for item_id, item_value in signature.items():
                new_item_id = item_id_map[item_id]
                new_signature[new_item_id] = item_value
            signature = new_signature

            self.env['sign.log'].create({'sign_request_id': sign_request.id, 'action': 'update'})
            body = _("The signature request has been edited by: %s.", self.partner_id.name)
            sign_request.message_post(body=body)

        self._sign(signature, **kwargs)

    def _sign(self, signature, **kwargs):
        """ Stores the sign request item values.
        :param signature: dictionary containing signature values and corresponding ids / signature image
        :param validation_required: boolean indicating whether the sign request item will after a further validation process or now
        """
        self.ensure_one()
        if not self.env.su:
            raise UserError(_("This function can only be called with sudo."))
        elif self.state != 'sent' or self.sign_request_id.state != 'sent':
            raise UserError(_("This sign request item cannot be signed"))
        elif self.sign_request_id.validity and self.sign_request_id.validity < fields.Date.today():
            raise UserError(_('This sign request is not valid anymore'))

        required_ids = set(self.sign_request_id.template_id.sign_item_ids.filtered(
            lambda r: r.responsible_id.id == self.role_id.id and r.required).ids)
        signature_ids = {int(k) for k in signature} if isinstance(signature, dict) else set()
        if not (required_ids <= signature_ids):  # Security check
            raise UserError(_("Some required items are not filled"))

        self._fill(signature, **kwargs)
        if not kwargs.get('validation_required', False):
            self._post_fill_request_item()

    def _send_no_credits_email(self):
        partner_lang = get_lang(self.env, lang_code=self.create_uid.partner_id.lang).code
        body = self.env['ir.qweb']._render('sign.sign_template_mail_not_enough_credits', {
            'record': self,
            'recipient_name': self.create_uid.name,
            'subject': '%s signed' % self.reference,
            'signer': self.partner_id,
            'auth_method': dict(self.role_id._fields['auth_method']._description_selection(self.env))[self.role_id.auth_method]
        }, lang=partner_lang, minimal_qcontext=True)

        self.env['sign.request']._message_send_mail(
            body, 'sign.sign_mail_notification_light',
            {'record_name': self.reference},
            {'model_description': 'signature',
             'company': self.communication_company_id or self.create_uid.company_id,
             'partner': self.create_uid.partner_id},
            {
                'email_from': self.create_uid.email_formatted,
                'author_id': self.create_uid.partner_id.id,
                'email_to': self.create_uid.email_formatted,
                'subject': _('%s: missing credits for extra-authentication', self.reference)
            },
            force_send=True,
            lang=partner_lang,
        )

    def _post_fill_request_item(self):
        self.env['sign.log'].create({'sign_request_item_id': self.id, 'action': 'sign'})
        self.write({'signing_date': fields.Date.context_today(self), 'state': 'completed'})
        if self.signed_without_extra_auth:
            self._send_no_credits_email()

        # mark signature as done in next activity
        if not self.sign_request_id.request_item_ids.filtered(lambda sri: sri.partner_id == self.partner_id and sri.state == 'sent'):
            sign_user = self.partner_id.user_ids[:1]
            if sign_user and sign_user.has_group('sign.group_sign_user'):
                self.sign_request_id.activity_feedback(['mail.mail_activity_data_todo'], user_id=sign_user.id)
        sign_request = self.sign_request_id
        if all(sri.state == 'completed' for sri in sign_request.request_item_ids):
            sign_request._sign()
        elif all(sri.state == 'completed' for sri in sign_request.request_item_ids.filtered(lambda sri: sri.mail_sent_order == self.mail_sent_order)):
            sign_request.send_signature_accesses()

    def _fill(self, signature, **kwargs):
        """ Stores the sign request item values. (Can be used to pre-fill the document as a hack)
        :param signature: dictionary containing signature values and corresponding ids / signature image
        """
        self.ensure_one()
        if not self.env.su:
            raise UserError(_("This function can only be called with sudo."))
        if self.state != 'sent' or self.sign_request_id.state != 'sent':
            raise UserError(_("This sign request item cannot be filled"))

        authorised_ids = set(self.sign_request_id.template_id.sign_item_ids.filtered(lambda r: r.responsible_id.id == self.role_id.id).ids)
        signature_ids = {int(k) for k in signature} if isinstance(signature, dict) else set()
        if not (signature_ids <= authorised_ids):
            raise UserError(_("Some unauthorised items are filled"))

        if not isinstance(signature, dict):
            self.signature = signature
        else:
            SignItemValue = self.env['sign.request.item.value']
            sign_request = self.sign_request_id
            new_item_values_list = []
            item_values_dict = {str(sign_item_value.sign_item_id.id): sign_item_value for sign_item_value in self.sign_item_value_ids}
            signature_item_ids = set(sign_request.template_id.sign_item_ids.filtered(lambda r: r.type_id.item_type == 'signature').ids)
            for itemId in signature:
                frame = kwargs.get('frame', False)
                if frame and itemId in frame:
                    frame_value = frame[itemId].get('frameValue', False)
                    frame_has_hash = bool(frame[itemId].get('frameHash', False))
                else:
                    frame_value = False
                    frame_has_hash = False
                if itemId not in item_values_dict:
                    new_item_values_list.append({'sign_item_id': int(itemId), 'sign_request_id': sign_request.id,
                                                 'value': signature[itemId], 'frame_value': frame_value,
                                                 'frame_has_hash': frame_has_hash, 'sign_request_item_id': self.id})
                else:
                    item_values_dict[itemId].write({
                        'value': signature[itemId], 'frame_value': frame_value, 'frame_has_hash': frame_has_hash
                    })
                if int(itemId) in signature_item_ids:
                    self.signature = signature[itemId][signature[itemId].find(',') + 1:]
            SignItemValue.create(new_item_values_list)

    def send_signature_accesses(self):
        self.sign_request_id._check_senders_validity()
        users = self.partner_id.user_ids
        user_ids = set(users.sudo().search([('all_group_ids', 'in', self.env.ref('sign.group_sign_user').id), ('id', 'in', users.ids)]).ids)
        for sign_request, sign_request_items_list in groupby(self, lambda sri: sri.sign_request_id):
            notified_users = [sri.partner_id.user_ids[:1]
                              for sri in sign_request_items_list
                              if not sri.is_mail_sent and sri.state == 'sent' and sri.partner_id.user_ids[:1].id in user_ids]
            sign_request._schedule_activity(notified_users)
            body = _("The signature mail has been sent to: ")
            receiver_names = ["%s(%s)" % (sri.partner_id.name, sri.role_id.name) for sri in sign_request_items_list]
            body += ', '.join(receiver_names)
            if not is_html_empty(sign_request.message):
                body += sign_request.message
            if not sign_request.communication_company_id:
                sign_request.communication_company_id = self.env.company
            sign_request.message_post(body=body, attachment_ids=sign_request.attachment_ids.ids)
        self._send_signature_access_mail()

    def _get_user_signature(self, signature_type='sign_signature'):
        """ Gets the user's stored sign_signature/sign_initials (needs sudo permission)
            :param str signature_type: 'sign_signature' or 'sign_initials'
            :returns bytes or False
        """
        self.ensure_one()
        sign_user = self.partner_id.user_ids[:1]
        if sign_user and signature_type in ['sign_signature', 'sign_initials']:
            return sign_user[signature_type]
        return False

    def _get_user_signature_frame(self, signature_type='sign_signature_frame'):
        """ Gets the user's stored sign_signature/sign_initials (needs sudo permission)
            :param str signature_type: 'sign_signature' or 'sign_initials'
            :returns bytes or False
        """
        self.ensure_one()
        sign_user = self.partner_id.user_ids[:1]
        if sign_user and signature_type in ['sign_signature_frame', 'sign_initials_frame']:
            return sign_user[signature_type]
        return False

    def _reset_sms_token(self):
        for record in self:
            record.sms_token = randint(100000, 999999)

    def _send_sms(self):
        self._reset_sms_token()
        sms_values = [{'body': _('Your confirmation code is %s', rec.sms_token), 'number': rec.sms_number} for rec in self]
        self.env['sms.sms'].sudo().create(sms_values).send()

    def _compute_access_url(self):
        super()._compute_access_url()
        for signature_request in self:
            signature_request.access_url = '/my/signature/%s' % signature_request.id

    @api.model
    def _generate_expiry_link_timestamp(self):
        duration = int(self.env['ir.config_parameter'].sudo().get_param('sign.link_expiry_duration', 360))
        expiry_date = fields.Datetime.now() + timedelta(hours=duration)
        return int(expiry_date.timestamp())

    @api.model
    def _generate_expiry_signature(self, sign_request_item_id, timestamp):
        return hmac(self.env(su=True), "sign_expiration", (timestamp, sign_request_item_id))

    def _validate_expiry(self, exp_timestamp, exp_hash):
        """ Validates if the expiry code is still valid
        :param float exp_timestamp: a timestamp provided by the user in the URL params
        :param str exp_hash: code provided in the URL to be checked
        """
        self.ensure_one()
        if not (exp_timestamp and exp_hash):
            return False
        exp_timestamp = int(exp_timestamp)
        now = fields.Datetime.now().timestamp()
        if now > exp_timestamp:
            return False
        return consteq(exp_hash, self._generate_expiry_signature(self.id, exp_timestamp))

    @api.depends('state')
    def _compute_color(self):
        color_map = {"canceled": 0,
                     "sent": 0,
                     "completed": 10}
        for sign_request_item in self:
            sign_request_item.color = color_map[sign_request_item.state]

    @api.depends('partner_id.email')
    def _compute_email(self):
        for sign_request_item in self.filtered(lambda sri: sri.state == "sent" or not sri.signer_email):
            sign_request_item.signer_email = sign_request_item.partner_id.email_normalized

    def _get_auto_field_value(self, item_type):
        """ Return the automatic value of a sign item based on the linked model and partner access
        :return: str: auto_value
        """
        self.ensure_one()
        item_type_sudo = self.env['sign.item.type'].sudo().browse(item_type['id'])
        record = None
        if item_type_sudo.model_id.model == 'res.partner':
            record = self.partner_id
        else:
            linked_record = self.sign_request_id.reference_doc
            model = linked_record and self.env['ir.model']._get(linked_record._name)
            if not model or not model.is_mail_thread:
                return ''
            record = linked_record
        try:
            auto_field = record.mapped(item_type['auto_field'])
            auto_value = auto_field[0] if auto_field and not isinstance(auto_field, models.BaseModel) else ''
        except (KeyError, TypeError):
            auto_value = ""
        return auto_value
