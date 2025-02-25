{
    "name": "VoIP OnSIP",
    "description": """Enables VoIP compatibility with OnSIP.""",
    "category": "Hidden",
    "version": "1.0",
    "depends": ["voip"],
    "data": [
        "views/res_users_views.xml",
        "views/voip_provider_views.xml",
    ],
    "author": "Odoo S.A.",
    "license": "OEEL-1",
    "assets": {
        "web.assets_backend": [
            "voip_onsip/static/src/**/*",
        ],
        "web.assets_unit_tests": [
            "voip_onsip/static/tests/**/*",
        ],
    },
}
