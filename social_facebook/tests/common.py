# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from unittest.mock import patch

from odoo.addons.social_facebook.models.social_account import SocialAccount
from odoo.addons.social.tests.common import SocialCase


class SocialFacebookCommon(SocialCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(SocialAccount, '_compute_statistics', lambda x: None), \
             patch.object(SocialAccount, '_create_default_stream_facebook', lambda *args, **kwargs: None):
            super(SocialFacebookCommon, cls).setUpClass()
