from odoo import models, fields, api


class HREmployeePublic(models.Model):

    _inherit = 'hr.employee.public'

    emp_code = fields.Char(related="employee_id.emp_code", readonly=True)
    state = fields.Selection(related="employee_id.state", readonly=True)
    exit_date = fields.Date(related="employee_id.exit_date", readonly=True)
    probation_period = fields.Integer(related="employee_id.probation_period", readonly=True)
    notice_period = fields.Integer(related="employee_id.notice_period", readonly=True)
    grade_id = fields.Many2one(related="employee_id.grade_id", readonly=True)
    opt_for_attendance_mail = fields.Boolean(related="employee_id.opt_for_attendance_mail", readonly=True)

    religion = fields.Selection(related="employee_id.religion", readonly=True)
    section = fields.Char(related="employee_id.section", readonly=True)
    sponsor = fields.Char(related="employee_id.sponsor", readonly=True)
    employee_name_arabic = fields.Char(related="employee_id.employee_name_arabic", readonly=True)
    previous_employee_code = fields.Char(related="employee_id.previous_employee_code", readonly=True)
    attendance_report_range = fields.Selection(related="employee_id.attendance_report_range", readonly=True)
    need_to_log_timesheet = fields.Boolean(related="employee_id.need_to_log_timesheet", readonly=True)
    allow_overtime = fields.Boolean(related="employee_id.allow_overtime", readonly=True)

    emp_code_old = fields.Char(related="employee_id.emp_code_old", readonly=True)
    first_name_passport = fields.Char(related="employee_id.first_name_passport", readonly=True)
    middle_name_passport = fields.Char(related="employee_id.middle_name_passport", readonly=True)
    last_name_passport = fields.Char(related="employee_id.last_name_passport", readonly=True)
    date_of_joining = fields.Date(related="employee_id.date_of_joining", readonly=True)
    section = fields.Char(related="employee_id.section", readonly=True)
    civil_id = fields.Char(related="employee_id.civil_id", readonly=True)
    civil_expiry = fields.Date(related="employee_id.civil_expiry", readonly=True)
    passport_expiry_date = fields.Date(related="employee_id.passport_expiry_date", readonly=True)
    salary_pay_mode = fields.Char(related="employee_id.salary_pay_mode", readonly=True)
    bank_iban = fields.Char(related="employee_id.bank_iban", readonly=True)
    work_permit_position = fields.Char(related="employee_id.work_permit_position", readonly=True)
    work_permit_salary = fields.Char(related="employee_id.work_permit_salary", readonly=True)
    personal_contact_no = fields.Char(related="employee_id.personal_contact_no", readonly=True)
    personal_email_id = fields.Char(related="employee_id.personal_email_id", readonly=True)


class HREmployee(models.Model):

    _inherit = 'hr.employee'

    emp_code = fields.Char("Employee Code")
    grade_id = fields.Many2one("hr.employee.grade", string="Grade")
    exit_date = fields.Date(string="Exit Date", help="Last working day of the employee")
    probation_period = fields.Integer(string="Probation Period in Days", tracking=True)
    notice_period = fields.Integer(string="Notice Period in Days", tracking=True)
    opt_for_attendance_mail = fields.Boolean(string="Opt for Attendance Report Mail")
    state = fields.Selection(
        [
            ("joined", "Joined"),
            ("probation", "On Probation"),
            ("employment", "Employment"),
            ("notice_period", "Notice Period"),
            ("resigned", "Resigned"),
            ("terminated", "Terminated")
        ], string="Status", default="joined", required=True
    )

    religion = fields.Selection(
        [
            ("Christianity","Christianity"),
            ("Islam","Islam"),
            ("Irreligion","Irreligion"),
            ("Hinduism","Hinduism"),
            ("Buddhism","Buddhism"),
            ("Folk Religions","Folk Religions"),
            ("Sikhism","Sikhism"),
            ("Judaism","Judaism")
        ], string="Religion"
    )
    section = fields.Char(string="Section")
    sponsor = fields.Char(string="Sponsor")
    employee_name_arabic = fields.Char(string="Employee Name in Arabic")
    previous_employee_code = fields.Char(string="Previous Employee Code")

    employee_dependency_ids = fields.One2many("hr.employee.dependent", "employee_id")
    employee_emergency_ids = fields.One2many("hr.employee.emergency", "employee_id")
    employee_qualification_ids = fields.One2many("hr.employee.qualification", "employee_id")

    attendance_report_range = fields.Selection(
        [
            ('this_month', 'This Month'),
            ('last_month', 'Last Month')
        ], default='this_month', string='Report Range'
    )
    need_to_log_timesheet = fields.Boolean(string="Need to Log Timesheet", default=True)
    allow_overtime = fields.Boolean(string="Allow Overtime")

    emp_code_old = fields.Char(string="Old Employee Code")
    first_name_passport = fields.Char(string="First Name - Passport")
    middle_name_passport = fields.Char(string="Middle Name - Passport")
    last_name_passport = fields.Char(string="Last Name - Passport")
    date_of_joining = fields.Date(string="Date of Joining")
    section = fields.Char(string="Section")
    civil_id = fields.Char(string="Civil ID")
    civil_expiry = fields.Date(string="Civil ID Expiry")
    passport_expiry_date = fields.Date(string="Passport Expiry Date")
    salary_pay_mode = fields.Char(string="Salary Pay Mode")
    bank_iban = fields.Char(string="Bank IBAN")
    work_permit_position = fields.Char(string="Work Permit Position")
    work_permit_salary = fields.Char(string="Work Permit Salary")
    personal_contact_no = fields.Char(string="Personal Contact Number")
    personal_email_id = fields.Char(string="Personal Email ID")



    @api.model
    def create(self, values):
        if not values.get('emp_code'):
            values['emp_code'] = self.env[
                'ir.sequence'].next_by_code('jic.employee.sequence')
        return super(HREmployee, self).create(values)
