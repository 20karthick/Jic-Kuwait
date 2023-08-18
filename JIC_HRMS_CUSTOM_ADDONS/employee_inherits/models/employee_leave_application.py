from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date,time, timedelta
import calendar
import time


class EmployeeLeaveApplication(models.Model):
    _name = 'employee.leave.application'
    _description = 'Leave Application'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee',  required=True, string='Employee Name')
    emp_code = fields.Char(string='Employee Code', compute='_compute_employee_fields_get', store=True)
    job_title = fields.Char(string='Job Title', compute='_compute_employee_fields_get', store=True)
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_employee_fields_get', store=True)
    date_of_joining = fields.Date(string="Date of Joining", compute='_compute_employee_fields_get', store=True)
    department_id = fields.Many2one('hr.department', "Department", compute='_compute_employee_fields_get', store=True)
    manager_id = fields.Many2one('hr.employee', "Manager", compute='_compute_employee_fields_get', store=True)
    hr_id = fields.Many2one('hr.employee', "HR Manager", store=True)
    leave_category = fields.Selection([('annual_leave', 'Annual Leave'),
                                       ('maternity', 'Maternity'),
                                       ('emergency_leave', 'Emergency Leave'),
                                       ('haj', 'Haj'),
                                       ('paternity', 'Paternity'),
                                       ('other_leave', 'Other Leave')
                                       ], 'Leave Category', required=True, default="other_leave")
    other_leave = fields.Char(string='Please Specify')
    reason_for_leave = fields.Char(string='Reason for Leave')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    return_date = fields.Date('Return Date')
    leave_payment_mode = fields.Selection([('advance_pay', 'Advance Pay'),
                                       ('along_payroll', 'Along with Payroll'),
                                       ('no_pay', 'No Pay'),
                                       ], 'Leave Payment Mode', required=True, default="no_pay")
    employee_signature = fields.Binary(string="Employee’s Signature", required=True)
    emp_sig_date = fields.Date('Date', required=True)
    director_signature = fields.Binary(string="Direct Manager’s Name & Signature")
    dir_sig_date = fields.Date('Date')
    hod_signature = fields.Binary(string="HoD Name & Signature")
    hod_sig_date = fields.Date('Date')
    received_on = fields.Char(string='Received On')
    monthly_basic_salary = fields.Selection([('inr', 'INR'),
                                           ('kwd', 'KWD'),
                                           ], ' Monthly Basic Salary')
    clb = fields.Integer('Current Leave Balance', size=3)
    nldu = fields.Integer('No.of Leave Days used', size=3)
    cb = fields.Integer('Current Balance', size=3)
    bsd = fields.Integer('Basic Salary Days', size=3)
    bsd_salary = fields.Selection([('inr', 'INR'), ('kwd', 'KWD')], 'Monthly Basic Salary')
    lsd = fields.Integer('Leave Salary Days', size=3)
    lsd_salary = fields.Selection([('inr', 'INR'), ('kwd', 'KWD')], 'Monthly Basic Salary')
    other_payment = fields.Char('Other Payment', size=25)
    other_salary = fields.Selection([('inr', 'INR'), ('kwd', 'KWD')], 'Monthly Basic Salary')
    other_payment_details = fields.Text("Other Payments Details")

    hr_executive = fields.Binary(string="HR Executive")
    hr_manager = fields.Binary(string="HR Manager")
    af_manager = fields.Binary(string="Asst.Finance Manager")
    cfo = fields.Binary(string="CFO")
    state = fields.Selection([
            ("draft", "Draft"),
            ("hr_approve", "Hr"),
            ("manager_approve", "Manager"),
            ("approved", "Approved")], string="Status", default="draft")


    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("A record can only be deleted in draft state."))
        return super(EmployeeLeaveApplication, self).unlink()

    @api.depends('employee_id')
    def _compute_employee_fields_get(self):
        for rec in self:
            if rec.employee_id:
                rec.emp_code = rec.employee_id.emp_code
                rec.job_title = rec.employee_id.job_title
                rec.company_id = rec.employee_id.company_id.id
                rec.date_of_joining = rec.employee_id.date_of_joining
                rec.department_id = rec.employee_id.department_id.id
                rec.manager_id = rec.employee_id.parent_id.id

    def leave_submit(self):
        for rec in self:
            if rec.env.user.employee_id == rec.employee_id:
                rec.state = 'hr_approve'
            else:
                raise ValidationError(_("You can't Submit this document, Only can Approve this selected Employee"))


    def approve_by_hr(self):
        for rec in self:
            if rec.env.user.employee_id == rec.hr_id:
                rec.state = 'manager_approve'
            else:
                raise ValidationError(_("You can't Approve this document, Only can Approve this 'Hr' user."))
        return True


    def approve_by_manager(self):
        for rec in self:
            if rec.env.user.employee_id == rec.manager_id:
                rec.state = 'approved'
            else:
                raise ValidationError(_("You can't Approve this document, Only can Approve this 'Manager' user."))
        return True

    def action_draft(self):
        for rec in self:
            if rec.state == 'hr_approve':
                if self.env.user.employee_id == rec.hr_id:
                    rec.state = 'draft'
                else:
                    raise ValidationError(_("You can't Draft this document, Only can Reset this 'HR Manager' user."))
            if rec.state == 'manager_approve':
                if self.env.user.employee_id == rec.manager_id:
                    rec.state = 'draft'
                else:
                    raise ValidationError(_("You can't Draft this document, Only can Reset this 'Manger' user."))

        return True



