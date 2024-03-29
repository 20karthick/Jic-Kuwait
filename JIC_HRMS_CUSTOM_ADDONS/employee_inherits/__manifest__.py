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
    'depends': ['base', 'web', 'project', 'hr_attendance','hr_timesheet_approval', 'hr', 'auth_signup', 'mail', 'hr_holidays', 'hr_skills','hr_payroll_community', 'jic_hr_payroll'],
    'live_test_url': '',
    'data': ['security/ir.model.access.csv',
             'security/employee_security.xml',
             'views/employee_view.xml',
             'views/mail_template.xml',
             'views/header_footer.xml',
             'views/employee_leave_creation_view.xml',
             'views/employee_leave_allocation_view.xml',
             'views/employee_mail_template.xml',
             'views/user_employee_contracts_import_view.xml',
             'views/cron.xml',
             'views/employee_leave_application_view.xml',
             'views/d12_formula_views.xml',
             'data/attendance_rules.xml'],

    'assets': {
        'web.assets_backend': [
            '/employee_inherits/static/src/js/action.js',
            # '/employee_inherits/static/src/js/project_js.js',
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
