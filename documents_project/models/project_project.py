# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import _, frozendict


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project']

    use_documents = fields.Boolean("Documents", default=True)
    documents_folder_id = fields.Many2one(
        'documents.document', string="Folder", copy=False, context=lambda env: {
            'default_folder_id': env.company.documents_project_folder_id.id,
        },
        domain="[('type', '=', 'folder'), ('shortcut_document_id', '=', False), "
               "'|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Folder in which all of the documents of this project will be categorized. All of the attachments of "
             "your tasks will be automatically added as documents in this workspace as well.")
    documents_tag_ids = fields.Many2many(
        'documents.tag', 'project_documents_tag_rel', string="Default Tags", copy=True)
    document_count = fields.Integer(
        compute='_compute_documents', export_string_translation=False)
    document_ids = fields.One2many('documents.document', compute='_compute_documents', export_string_translation=False)

    @api.ondelete(at_uninstall=False)
    def _archive_folder_on_projects_unlinked(self):
        """ Archives the project folder if all its related projects are unlinked. """
        self.env['documents.document'].sudo().search([
            ('project_ids', '!=', False),
            ('project_ids', 'not any', [('id', 'not in', self.ids)]
        )]).sudo(False)._filtered_access('unlink').action_archive()

    @api.constrains('documents_folder_id')
    def _check_company_is_folders_company(self):
        for project in self.filtered('documents_folder_id'):
            if folder := project['documents_folder_id']:
                if folder.company_id and project.company_id != folder.company_id:
                    raise UserError(_(
                        'The "%(folder)s" folder should either be in the "%(company)s" company like this'
                        ' project or be open to all companies.',
                        folder=folder.name, company=project.company_id.name)
                    )

    def _compute_documents(self):
        documents = self.env['documents.document'].search([
            ('type', 'in', ('binary', 'url')),
            ('id', 'child_of', self.documents_folder_id.ids)
        ])
        for project in self:
            if not project.use_documents:
                project.document_ids = self.env['documents.document']
                project.document_count = 0
                continue
            document_ids = documents.filtered(lambda doc: doc.parent_path.startswith(project.documents_folder_id.parent_path))
            project.document_ids = document_ids
            project.document_count = len(document_ids)

    def _create_missing_folders(self):
        folders_to_create_vals = []
        projects_with_folder_to_create = []
        documents_project_folder_id = self.env.company.documents_project_folder_id.id

        for project in self:
            if not project.documents_folder_id:
                folder_vals = {
                    'access_internal': 'edit' if project.privacy_visibility != 'followers' else 'none',
                    'company_id': project.company_id.id,
                    'folder_id': documents_project_folder_id,
                    'name': project.name,
                    'type': 'folder',
                }
                folders_to_create_vals.append(folder_vals)
                projects_with_folder_to_create.append(project)

        if folders_to_create_vals:
            created_folders = self.env['documents.document'].sudo().create(folders_to_create_vals)
            for project, folder in zip(projects_with_folder_to_create, created_folders):
                project.sudo().documents_folder_id = folder

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        if not self.env.context.get('no_create_folder'):
            projects.filtered(lambda project: project.use_documents)._create_missing_folders()
        return projects

    def write(self, vals):
        if 'company_id' in vals:
            for project in self:
                if project.documents_folder_id and project.documents_folder_id.company_id and len(project.documents_folder_id.project_ids) > 1:
                    other_projects = project.documents_folder_id.project_ids - self
                    if other_projects and other_projects.company_id.id != vals['company_id']:
                        lines = [f"- {project.name}" for project in other_projects]
                        raise UserError(_(
                            'You cannot change the company of this project, because its workspace is linked to the other following projects that are still in the "%(other_company)s" company:\n%(other_workspaces)s\n\n'
                            'Please update the company of all projects so that they remain in the same company as their workspace, or leave the company of the "%(workspace)s" workspace blank.',
                            other_company=other_projects.company_id.name, other_workspaces='\n'.join(lines), workspace=project.documents_folder_id.name))

        if 'name' in vals and len(self.documents_folder_id.sudo().project_ids) == 1 and self.name == self.documents_folder_id.sudo().name:
            self.documents_folder_id.sudo().name = vals['name']

        if new_visibility := vals.get('privacy_visibility'):
            (self.documents_folder_id | self.document_ids).action_update_access_rights(
                access_internal='none' if new_visibility == 'followers' else 'edit')
        project_root_documents = self.env['documents.document']
        if 'documents_folder_id' in vals:
            project_root_documents = self.documents_folder_id.children_ids

        res = super().write(vals)
        if 'company_id' in vals:
            for project in self:
                if project.documents_folder_id and project.documents_folder_id.company_id:
                    project.documents_folder_id.company_id = project.company_id
        if not self.env.context.get('no_create_folder'):
            self.filtered('use_documents')._create_missing_folders()
        if project_root_documents:
            project_root_documents.folder_id = self.documents_folder_id

        return res

    def copy(self, default=None):
        # We have to add no_create_folder=True to the context, otherwise a folder
        # will be automatically created during the call to create.
        # However, we cannot use with_context, as it instantiates a new recordset,
        # and this copy would call itself infinitely.
        previous_context = self.env.context
        self.env.context = frozendict(self.env.context, no_create_folder=True)
        copied_projects = super().copy(default)
        self.env.context = previous_context

        for old_project, new_project in zip(self, copied_projects):
            if not self.env.context.get('no_create_folder') and new_project.use_documents and old_project.documents_folder_id:
                new_project.documents_folder_id = old_project.documents_folder_id.with_context(
                    documents_copy_folders_only=True).sudo().copy(
                        {'name': new_project.name, 'owner_id': False}
                    )
        return copied_projects

    def _get_stat_buttons(self):
        buttons = super()._get_stat_buttons()
        if self.use_documents and self.documents_folder_id.user_permission != 'none':
            buttons.append({
                'icon': 'file-text-o',
                'text': self.env._('Documents'),
                'number': self.document_count,
                'action_type': 'object',
                'action': 'action_view_documents_project',
                'additional_context': json.dumps({
                    'active_id': self.id,
                }),
                'show': self.use_documents,
                'sequence': 20,
            })
        return buttons

    def action_view_documents_project(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("documents.document_action_preference")
        return action | {
            'view_mode': 'kanban,list',
            'context': {
                'active_id': self.id,
                'active_model':  'project.project',
                'documents_unique_folder_id': True,
                'searchpanel_default_folder_id': self.documents_folder_id.id,
            }
        }
