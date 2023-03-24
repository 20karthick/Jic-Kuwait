# -*- coding: utf-8 -*-

{
    'name': 'Odoo 15 Base Module for Jobin International Company',
    'version': '15.0.1.0.0',
    'category': 'General',
    'description': 'Base Module for JIC IT projects ',
    'summary': 'Essential module for work with JIC Projects',
    'sequence': '1',
    'author': 'JIC IT Solutions',
    'license': 'LGPL-3',
    'company': 'JIC IT Solutions',
    'maintainer': 'JIC',
    'support': 'jic@gmail.com',
    'website': 'https://www.jic.com',
    'depends': ['base','web','project', 'hr', 'auth_signup', 'mail', 'hr_holidays','hr_skills'],
    'live_test_url': '',
    'data': ['views/employee_view.xml',
             'views/mail_template.xml',
             'views/header_footer.xml',
             'security/employee_security.xml',],

    'assets': {
        'web.assets_backend': [
            '/employee_inherits/static/src/js/action.js',
        ],
        'web.assets_qweb': [

            ],
    },

    'pre_init_hook': '',
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
