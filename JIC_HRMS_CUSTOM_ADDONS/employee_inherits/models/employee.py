from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.http import request

# class HrEmployeeInherits(models.Model):
#     _inherit = 'hr.employee'
#
#     wage = fields.Float(string="Wage", compute='_compute_employee_salary')
#     hra = fields.Float(string='HRA', help="House rent allowance.", compute='_compute_employee_salary')
#     travel_allowance = fields.Float(string="Travel Allowance", help="Travel allowance", compute='_compute_employee_salary')
#     da = fields.Float(string="DA", help="Dearness allowance", compute='_compute_employee_salary')
#     meal_allowance = fields.Float(string="Meal Allowance", help="Meal allowance", compute='_compute_employee_salary')
#     medical_allowance = fields.Float(string="Medical Allowance", help="Medical allowance", compute='_compute_employee_salary')
#     other_allowance = fields.Float(string="Other Allowance", help="Other allowances", compute='_compute_employee_salary')
#     employee_contribution_perc = fields.Float(string="Employee Contribution %", compute='_compute_employee_salary')
#     employer_contribution_perc = fields.Float(string="Employer Contribution %", compute='_compute_employee_salary')
#     employee_leave_details_ids = fields.Many2many('hr.leave', string="Employee Leave Information")
#     uan = fields.Integer(string="UAN Number")
#     esi = fields.Integer(string="ESI Number")
#     wwf = fields.Integer(string="WWF Number")
#
#     present_address = fields.Char(string="Present Address")
#     aadhar_number = fields.Char(string="Aadhar Number")
#     pan = fields.Char(string="PAN Number")
#     father_name = fields.Char(string="Father Name")
#     mother_name = fields.Char(string="Mother Name")
#
#     ifsc = fields.Char(string="IFSC Code")
#     last_working_day = fields.Date(string="Date of Last Working Day")
#     date_of_resignation = fields.Date(string="Date of Resignation")
#     date_of_promotions = fields.Date(string="Date of Promotions")
#     date_of_increments = fields.Date(string="Date of Increments")
#     date_of_probation = fields.Date(string="Date of Probation Confirmation")
#     employee_bank_name = fields.Char(string="Employee Bank Name")
#
#     misc_allowance = fields.Float(string="Misc.Allowance")
#     variable_inc = fields.Float(string="Variable Inc")
#     arrears = fields.Float(string="Arrears")
#     other_earnings = fields.Float(string="Other Earnings")
#     incentive = fields.Float(string="Incentive")
#     gmi_release = fields.Float(string="GMI Release")
#
#
#
#     def _compute_employee_salary(self):
#         for rec in self:
#             rec.wage = rec.contract_id.wage
#             rec.hra = rec.contract_id.hra
#             rec.travel_allowance = rec.contract_id.travel_allowance
#             rec.da = rec.contract_id.da
#             rec.meal_allowance = rec.contract_id.meal_allowance
#             rec.medical_allowance = rec.contract_id.medical_allowance
#             rec.other_allowance = rec.contract_id.other_allowance
#             rec.employee_contribution_perc = rec.contract_id.employee_contribution_perc
#             rec.employer_contribution_perc = rec.contract_id.employer_contribution_perc
#             rec.misc_allowance = rec.contract_id.misc_allowance
#             rec.variable_inc = rec.contract_id.variable_inc
#             rec.arrears = rec.contract_id.arrears
#             rec.other_earnings = rec.contract_id.other_earnings
#             rec.incentive = rec.contract_id.incentive
#             rec.gmi_release = rec.contract_id.gmi_release
#



class HrContractInherits(models.Model):
    _inherit = 'hr.contract'

    misc_allowance = fields.Float(string="Misc.Allowance")
    variable_inc = fields.Float(string="Variable Inc")
    arrears = fields.Float(string="Arrears")
    other_earnings = fields.Float(string="Other Earnings")
    incentive = fields.Float(string="Incentive")
    gmi_release = fields.Float(string="GMI Release")
