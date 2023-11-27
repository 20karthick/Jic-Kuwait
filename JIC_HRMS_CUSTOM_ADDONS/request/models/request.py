from odoo import api, fields, models, tools, exceptions, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta, time
import json
from lxml import etree

class RequestApproverHistory(models.Model):
    _name = 'request.approver.history'

    request_id = fields.Many2one('employee.request', string="Employee Request")
    from_stage_id = fields.Many2one('request.stage', string="From Stage")
    to_stage_id = fields.Many2one('request.stage', string="To Stage")
    user_id = fields.Many2one('res.users', string="Users")


class EmployeeRequest(models.Model):
    _name = 'employee.request'
    _rec_name = 'employee_id'
    _description = "Request"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']

    # def _default_stage_id(self):
    #     # Since project stages are order by sequence first, this should fetch the one with the lowest sequence number.
    #     return self.env['request.stage'].search([('request_type', '=', self.request_type)],limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    emp_code = fields.Char(string='Employee Code', compute='_compute_get_employee_details', store=True)
    job_title = fields.Char(string='Job Title', compute='_compute_get_employee_details', store=True)
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_get_employee_details', store=True)
    date_of_joining = fields.Date(string="Date of Joining", compute='_compute_get_employee_details', store=True)
    department_id = fields.Many2one('hr.department', "Department", compute='_compute_get_employee_details', store=True)
    manager_id = fields.Many2one('hr.employee', "Line Manager", compute='_compute_get_employee_details', store=True)
    request_type = fields.Selection([('rt_rr', 'Residence Transfer/ Renewal Request'),
                                     ('cp', 'Change in Pay'),
                                     ('maf', 'Mobile Acknowledgment'),
                                     ('paf', 'Passport Acknowledgment'),
                                     ('prf', 'Passport Release'),
                                     ('saf', 'Salary Advance'),
                                     ('vhf', 'Vehicle Handover'),
                                     ('el', 'Experience Letter'),
                                     ('laf', 'Laptop Acknowledge'),
                                     ('ecf', 'Employee Clearance'),
                                     ('mrf', 'Manpower Requisition'),
                                     ('pai', 'Promotion and Increment'),
                                     ('pcl', 'Probation Confirmation letter with Salary'),
                                     ('pclws', 'Probation Confirmation letter without Salary'),
                                     ('prom', 'Promotion Letter (without Salary)'),
                                     ('ral', 'Resignation Acceptance Letter'),
                                     ('dl', 'Deputation Letter'),
                                     ('sc', 'Salary Certificate'),
                                     ('va', 'Vehicle Acknowledgement'),
                                     ('nlr', 'Notification of Leave Return'),
                                     ('lrf', 'Loan Request'),
                                     ('nol', 'No Objection Letter to Embassy'),
                                     ('ic', 'Internship Certificate'),
                                     ('taf', 'Tablet Acknowledgment Form'),
                                       ], 'Request Type', required=True)
    stage_id = fields.Many2one('request.stage', string='Stage', compute='_compute_stage_id',
                               store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                               domain="[('request_type', '=', request_type),('company_id', '=', company_id)]", copy=False, task_dependency_tracking=True)
    invisible_buttons = fields.Boolean(string="Buttons")
    inv_submit = fields.Boolean(string="Submit Buttons", default=True, compute='_compute_submit')
    user_id = fields.Many2one("res.users", string='User', compute='_compute_get_employee_details', tracking=True, store=True)
    submit = fields.Integer(string="submit")
    user_name = fields.Char(string='User Name')
    civil_id = fields.Char(string='Civil ID', compute='_compute_get_employee_details', store=True)
    passport_id = fields.Char(string='Passport ID', compute='_compute_get_employee_details', store=True)
    stage_ids = fields.Many2many('request.stage', string='Stages')
    request_date = fields.Datetime(string='Request Date', compute='_compute_get_employee_details', store=True)

    civil_passport_join = fields.Char(string='civil Passport join', compute='_join_civil_passport', store=True)
    approver_ids = fields.One2many('request.approver.history', 'request_id', string='Approved Stage', copy=True)

    @api.depends('civil_id', 'passport_id')
    def _join_civil_passport(self):
        for req in self:
            if req.civil_id and not req.passport_id:
                req.civil_passport_join = req.civil_id
            elif req.passport_id and not req.civil_id:
                req.civil_passport_join = req.passport_id
            else:
                if req.civil_id and req.passport_id:
                    req.civil_passport_join = " / ".join([req.civil_id, req.passport_id])



    def print_report(self):
        if self.request_type == 'rt_rr':
            return self.env.ref('request.action_residence_transfer_renewal_request').report_action(self)
        elif self.request_type == 'cp':
            return self.env.ref('request.action_report_change_in_pay_request').report_action(self)
        elif self.request_type == 'maf':
            return self.env.ref('request.action_mobile_acknowledgment_request').report_action(self)
        elif self.request_type == 'paf':
            return self.env.ref('request.action_passport_acknowledgment_request').report_action(self)
        elif self.request_type == 'prf':
            return self.env.ref('request.action_passport_release_request').report_action(self)
        elif self.request_type == 'saf':
            return self.env.ref('request.action_salary_advance_request').report_action(self)
        elif self.request_type == 'vhf':
            return self.env.ref('request.action_vehicle_handover_request').report_action(self)
        elif self.request_type == 'el':
            return self.env.ref('request.action_experience_letter_request').report_action(self)
        elif self.request_type == 'laf':
            return self.env.ref('request.action_laptop_acknowledge_request').report_action(self)
        elif self.request_type == 'ecf':
            return self.env.ref('request.action_employee_clearance_request').report_action(self)
        elif self.request_type == 'mrf':
            return self.env.ref('request.action_manpower_requisition_request').report_action(self)
        elif self.request_type == 'pai':
            return self.env.ref('request.action_promotion_increment_letter_request').report_action(self)
        elif self.request_type == 'pcl':
            return self.env.ref('request.action_probation_confirmation_letter_request').report_action(self)
        elif self.request_type == 'pclws':
            return self.env.ref('request.action_probation_confirmation_without_salary').report_action(self)
        elif self.request_type == 'prom':
            return self.env.ref('request.action_promotion_letter_without_salary_request').report_action(self)
        elif self.request_type == 'ral':
            return self.env.ref('request.action_resignation_acceptance_request').report_action(self)
        elif self.request_type == 'dl':
            return self.env.ref('request.action_deputation_letter').report_action(self)
        elif self.request_type == 'sc':
            return self.env.ref('request.action_report_salary_certificate').report_action(self)
        elif self.request_type == 'va':
            return self.env.ref('request.action_vehicle_acknowledgement').report_action(self)
        elif self.request_type == 'nlr':
            return self.env.ref('request.action_notification_of_leave_return').report_action(self)
        elif self.request_type == 'nol':
            return self.env.ref('request.action_promotion_increment_letter_request').report_action(self)
        elif self.request_type == 'ic':
            return self.env.ref('request.action_internship_certificate').report_action(self)
        elif self.request_type == 'taf':
            return self.env.ref('request.action_tablet_acknowledgment').report_action(self)
        else:
            raise UserError(_("There is no pdf Report."))

    @api.depends('request_type')
    def _compute_submit(self):
        for task in self:
            if task.stage_id.id == task.submit:
                task.inv_submit = True
            else:
                task.inv_submit = False


    def reject(self):
        sequence = self.stage_id.sequence
        seq_number = sequence - 1
        stage = self.env['request.stage'].search([('request_type', '=', self.request_type),('company_id', '=', self.company_id.id), ('sequence', '=', seq_number)], limit=1)
        if stage:
            if self.stage_id.line_manager:
                manager = self.employee_id.parent_id
                if manager.user_id == self.env.user:
                    self.env["request.approver.history"].search([('request_id', '=', self.id), ('from_stage_id', '=', stage.id), ('to_stage_id', '=', self.stage_id.id)]).unlink()
                    self.stage_id = stage.id
                    self.invisible_buttons = False
                else:
                    raise UserError(_("Only %s Line Manager can refuse it.", manager.name))

            if self.stage_id.department:
                if self.stage_id.department == self.env.user.department:
                    self.env["request.approver.history"].search([('request_id', '=', self.id), ('from_stage_id', '=', stage.id), ('to_stage_id', '=', self.stage_id.id)]).unlink()
                    self.stage_id = stage.id
                    self.invisible_buttons = False
                else:
                    raise UserError(_("Only %s Department user can refuse it.", self.stage_id.department))
        else:
            raise UserError(_("Already you are in requesting stage."))


    def approve(self):
        if self.stage_id and self.request_type:
            if self.stage_id.start_stage:
                if self.user_id == self.env.user:
                    seq = self.stage_id.sequence
                    seq_number = seq + 1
                    stage = self.env['request.stage'].search([('request_type', '=', self.request_type), ('company_id', '=', self.company_id.id),('sequence', '=', seq_number)], limit=1)
                    if not self.stage_id.start_stage and not self.stage_id.end_stage:
                        self.stage_ids = [(4, self.stage_id.id)]
                    if stage:
                        self.stage_id = stage.id
                        self.invisible_buttons = False
                        if stage.end_stage == True:
                            self.invisible_buttons = True

                    else:
                        self.stage_id = self.stage_id
                        if not self.invisible_buttons:
                            raise UserError(_("Kindly check the stage Sequence or enable which one is end stage."))
                else:
                    raise UserError(_("Only selected employee can submit / Approve from user."))


            elif self.stage_id.line_manager:
                manager = self.employee_id.parent_id
                if not manager:
                    raise UserError(_("Manager Not Mapped For requested employee(%s)", self.employee_id.name))

                if manager.user_id == self.env.user:
                    seq = self.stage_id.sequence
                    seq_number = seq + 1
                    stage = self.env['request.stage'].search([('request_type', '=', self.request_type),('company_id', '=', self.company_id.id), ('sequence', '=', seq_number)], limit=1)
                    if not self.stage_id.start_stage and not self.stage_id.end_stage:
                        self.stage_ids = [(4, self.stage_id.id)]
                    if stage:
                        self.approver_ids.create({
                            'request_id': self.id,
                            'from_stage_id': self.stage_id.id,
                            'to_stage_id': stage.id,
                            'user_id': self.env.user.id,
                        })
                        self.stage_id = stage.id
                        self.invisible_buttons = False
                        if stage.end_stage == True:
                            self.invisible_buttons = True

                    else:
                        self.stage_id = self.stage_id
                        if not self.invisible_buttons:
                            raise UserError(_("Kindly check the stage Sequence or enable which one is end stage."))
                else:
                    raise UserError(_("Only Line Manager can approve it."))

            elif self.stage_id.department:
                department = self.stage_id.department
                if department == self.env.user.department:
                    seq = self.stage_id.sequence
                    seq_number = seq + 1
                    stage = self.env['request.stage'].search([('request_type', '=', self.request_type),('company_id', '=', self.company_id.id), ('sequence', '=', seq_number)], limit=1)
                    if not self.stage_id.start_stage and not self.stage_id.end_stage:
                        self.stage_ids = [(4, self.stage_id.id)]
                    if stage:
                        self.approver_ids.create({
                            'request_id': self.id,
                            'from_stage_id': self.stage_id.id,
                            'to_stage_id': stage.id,
                            'user_id': self.env.user.id,
                        })
                        self.stage_id = stage.id
                        self.invisible_buttons = False
                        if stage.end_stage == True:
                            self.invisible_buttons = True

                    else:
                        self.stage_id = self.stage_id
                        if not self.invisible_buttons:
                            raise UserError(_("Kindly check the stage Sequence or enable which one is end stage."))
                else:
                    raise UserError(_("Only %s Department user can approve it.", self.stage_id.department))
        else:
            raise UserError(_("Check whether request stages or request type exists in this request or not. If not inform to HR."))

    @api.depends('request_type')
    def _compute_stage_id(self):
        for task in self:
            if task.employee_id:
                if task.request_type:
                    if task.request_type != task.stage_id.request_type:
                        # task.stage_id = self.env['request.stage'].search([('request_type', '=', 'request_type'),])
                        task.stage_id = task.stage_find(task.request_type, [])
                        self.submit = task.stage_id.id
                else:
                    task.stage_id = False

    def stage_find(self, request, domain=[], order='sequence, id'):
        request_ids = []
        if request:
            request_ids.append(request)
        request_ids.extend(self.mapped('request_type'))
        search_domain = []
        if request_ids:
            search_domain = [('|')] * (len(request_ids) - 1)
            for rec in request_ids:
                search_domain.append(('request_type', '=', rec))
                search_domain.append(('company_id', '=', self.company_id.id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['request.stage'].search(search_domain, order=order, limit=1).id

    @api.depends('employee_id')
    def _compute_get_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.emp_code = rec.employee_id.emp_code
                rec.job_title = rec.employee_id.job_title
                rec.company_id = rec.employee_id.company_id.id
                rec.date_of_joining = rec.employee_id.date_of_joining
                rec.department_id = rec.employee_id.department_id.id
                rec.manager_id = rec.employee_id.parent_id.id
                rec.user_id = rec.employee_id.user_id.id
                rec.user_name = rec.user_id.name
                rec.civil_id = rec.employee_id.civil_id
                rec.passport_id = rec.employee_id.passport_id
                rec.request_date = fields.Datetime.now()

    # Residence Transfer / Renewal Request
    probation_completed = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Probation Completed',tracking=True)
    basic_salary = fields.Char(string="Basic Salary", tracking=True)
    work_permit_salary = fields.Char(string="Work Permit Salary", tracking=True)
    no_of_years = fields.Selection([('one', '1'), ('two', '2')], 'No. of Years', tracking=True)
    basic_salary_renewal = fields.Char(string="Basic Salary", tracking=True)
    work_permit_salary_renewal = fields.Char(string="Work Permit Salary", tracking=True)

    # Change in Pay
    current_job_title = fields.Char(string='Current Job Title', related='job_title', tracking=True)
    change_job_title = fields.Char(string='Change in Job Title(if applicable)', tracking=True)
    existing_basic_salary = fields.Char(string="Basic Salary", tracking=True)
    existing_add_allowance = fields.Char(string="Additional Allowance", tracking=True)
    existing_gross_salary = fields.Char(string="Gross Salary", tracking=True)
    revision_basic_salary = fields.Char(string="Basic Salary", tracking=True)
    revision_add_allowance = fields.Char(string="Additional Allowance", tracking=True)
    revision_gross_salary = fields.Char(string="Gross Salary", tracking=True)
    revised_date = fields.Date(string="Revised Pay Effective Date", tracking=True)
    justification = fields.Text(string="Justification / Reasons", tracking=True)

    # Mobile Acknowledgment Form
    manufactured_by = fields.Char(string="Manufactured By", tracking=True)
    model_name = fields.Char(string="Model Name", tracking=True)
    model_no = fields.Char(string="Model No.", tracking=True)
    serial_no = fields.Char(string="Serial No.", tracking=True)
    imei_code_1 = fields.Char(string="IMEI Code", tracking=True)
    imei_code_2 = fields.Char(string="IMEI Code", tracking=True)
    accessories = fields.Char(string="Accessories", help="Accessories Provided to Employee with Company Phone", tracking=True)
    description = fields.Text(string="Description", default="1. This phone is exclusively a property of Jobin International Company and is given to you solely for JIC Group business purposes. \n " 
                                                            "2. The main purpose of this company phone is to respond to JIC clients or business associates during working hours and also as per the need of the hour. Hence the handset should be charged fully & kept ON for receiving calls and messages always. \n "
                                                            "3. No excuses will be accepted if you could not be contacted for reason stating phone was switched OFF or for low battery. This will be taken seriously. \n "
                                                            "4. It is your responsibility to take care of the above-mentioned device with accessories (Mobile Cover, USB cable, power adaptor) and SIM card. Make sure of NO damage to the handset or SIM card. \n"
                                                            "5. JIC pays for local calls & internet usage, and JIC is not responsible for any international call charges or international roaming charges over & any other charges other than what is specified here. \n"
                                                            "6. When you are proceeding on your annual leave or at the event of leaving the organization, the phone, its accessories (Mobile Cover, USB cable, power adaptor) & SIM card should be returned to the office", tracking=True)


    # Passport Acknowledgment Form
    nationality_id = fields.Many2one("res.country", string="Nationality", tracking=True)
    office_location = fields.Char(string="Office Location", tracking=True)
    handover_id = fields.Many2one('hr.department', "Handover The passport To", tracking=True)
    handed_over_date = fields.Datetime(string="Handover Date", tracking=True)

    # Passport Release Form
    release_nationality_id = fields.Many2one("res.country", string="Nationality", tracking=True)
    company_location = fields.Char(string="Company Location", tracking=True)
    reason = fields.Char(string="Handover The passport To", tracking=True)
    passport_return_date = fields.Char(string="Tentative Passport Return Date", tracking=True)
    return_by = fields.Char(string="Returned By", tracking=True)
    return_date = fields.Datetime(string="Date", tracking=True)

    # salary Advance Form
    monthly_salary = fields.Char(string="Monthly Basic Salary:INR/KWD", tracking=True)
    advance_request_date = fields.Datetime(string="Request Date", tracking=True)
    reason_for_advance = fields.Char(string="Reason For Advance", tracking=True)
    request_amount = fields.Char(string="Advance Salary Amount Request: INR/KWD", tracking=True)

    # Vehicle Handover Form
    v_name = fields.Char(string="Name", tracking=True)
    v_civil_id = fields.Char(string="Civil ID", tracking=True)
    vehicle_reg_no = fields.Char(string="Vehicle Reg. No.", tracking=True)
    make_model = fields.Char(string="Make / Model", tracking=True)
    odometer = fields.Char(string="Odometer Reading :kms", tracking=True)
    handover_date = fields.Datetime(string="Handover Date & Time", tracking=True)
    vehicle_handover_to = fields.Char(string="Vehicle Handover to", tracking=True)
    inspection_done = fields.Char(string="Inspection Done By", tracking=True)
    inspection_comments = fields.Char(string="Inspection Comments", tracking=True)

    # Experience Letter
    title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    emp_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    last_working_date = fields.Date(string="Last Working Date", tracking=True)

    # Laptop Acknowledge Form
    laf_date = fields.Date(string="Date", tracking=True)
    laf_employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    laf_company = fields.Char(string="Company", tracking=True)
    laf_model_type = fields.Char(string="Model / Type", tracking=True)
    laf_serial_no = fields.Char(string="Serial No.", tracking=True)
    laf_color = fields.Char(string="Color", tracking=True)
    laf_charger = fields.Char(string="Charger", tracking=True)
    laf_keyboard = fields.Char(string="Keyboard", tracking=True)
    laf_mouse = fields.Char(string="Mouse", tracking=True)
    laf_laptop_bag = fields.Char(string="Laptop Bag", tracking=True)

    #Employee Clearance Form
    ecf_reason_for_leave = fields.Selection([('ter', 'Termination'), ('res', 'Resignation')], 'Reason For Leaving', tracking=True)
    ecf_accommodation = fields.Char(string="Accommodation", tracking=True)
    ecf_fleet_transport = fields.Char(string="Fleet Transportation", tracking=True)
    ecf_office_key = fields.Char(string="Office Keys", tracking=True)
    ecf_access_card = fields.Char(string="Access Card", tracking=True)
    ecf_passport = fields.Char(string="Passport", tracking=True)
    ecf_work_permit = fields.Char(string="Working Permit", tracking=True)
    ecf_civil_id = fields.Char(string="Civil ID", tracking=True)
    ecf_clearance_certificate = fields.Char(string="Clearance Certificate(MoJ)", tracking=True, help="Clearance Certificate - Ministry of Justics")
    ecf_loans = fields.Char(string="Loans", tracking=True)
    ecf_advance = fields.Char(string="Advance", tracking=True)
    ecf_salary = fields.Char(string="Salary", tracking=True)
    ecf_petty_cash = fields.Char(string="Petty Cash", tracking=True)
    ecf_fuel_card = fields.Char(string="Fuel Card", tracking=True)
    ecf_traffic_fines = fields.Char(string="Traffic Fines", tracking=True)
    ecf_others = fields.Char(string="Others", tracking=True)
    ecf_attendance = fields.Char(string="Attendance", tracking=True)
    ecf_payroll = fields.Char(string="Payroll", tracking=True)
    ecf_id_card = fields.Char(string="ID Card", tracking=True)
    ecf_business_card = fields.Char(string="Business Cards", tracking=True)
    ecf_experience_certificate = fields.Char(string="Experience Certificate", tracking=True)
    ecf_manager_ack = fields.Char(string="Line Manager Ack.", tracking=True,help="Line Manager Acknowledgment")
    ecf_handover_confirmation = fields.Char(string="Handover Confirmation", tracking=True)
    ecf_laptop_pc = fields.Char(string="Laptop/PC", tracking=True)
    ecf_mobile_set = fields.Char(string="Mobile Set", tracking=True)
    ecf_sim_card = fields.Char(string="Sim Card", tracking=True)
    ecf_internet_router = fields.Char(string="Internet Router", tracking=True)
    ecf_other_it_asset = fields.Char(string="Other IT Assets", tracking=True)

    #manpower Requisition Form
    req_for_department = fields.Char(string="Requisition for Department", tracking=True)
    req_for_designation = fields.Char(string="Requisition for Designation", tracking=True)
    req_job = fields.Selection([('no', 'New Opening'), ('replacement', 'Replacement')], 'Job for', tracking=True)
    req_reason_for_requirement = fields.Char(string="Reason For Requirement", tracking=True)
    req_experience_min = fields.Char(string="Experience Min", tracking=True)
    req_experience_max = fields.Char(string="Experience Max", tracking=True)
    req_requesting_location = fields.Char(string="Requesting Location", tracking=True)
    req_vacancies = fields.Char(string="No.of Vacancies", tracking=True)
    req_reporting = fields.Char(string="Reporting / Line Manager", tracking=True)
    req_urgent = fields.Char(string="Reporting / Line Manager", tracking=True)
    req_designation = fields.Char(string="Designation", tracking=True)
    req_purpose = fields.Char(string="Purpose", tracking=True)
    req_Responsibilities = fields.Text(string="Responsibilities", tracking=True)
    req_technical_experience = fields.Text(string="Technical Experience", tracking=True)
    req_higher_secondary = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Up to Higher Secondary', tracking=True)
    req_diploma = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'If Technical Diploma', tracking=True)
    req_bachelor_degree = fields.Selection([('yes', 'YES'), ('no', 'NO')], "If Bachelor's Degree", tracking=True)
    req_master_degree = fields.Selection([('yes', 'YES'), ('no', 'NO')], "If Master's Degree", tracking=True)
    req_training_project = fields.Char(string="Training / Project Done", tracking=True)
    req_related_experience = fields.Selection([('af', 'Account / Finance'), ('qa', 'Quality Assurance'), ('se', 'Software Engineering'), ('te', 'Tool Engineering'),
                                    ('pd', 'Product Development'), ('marketing', 'Marketing'), ('mpl', 'Material Planning & Logistic'), ('rd', 'Research & Development'),
                                    ('purchase', 'Purchase'), ('pa', 'HR/Personnel & Administration'), ('cn', 'Computer & Networking'),('doc', 'Documentation'),
                                    ('coordination', 'Coordination'), ('np', 'No Preference'), ('other', 'Others')
                                    ], 'Preferred Related Experience', tracking=True)

    # Promotion and Increment
    pai_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    pai_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    pai_position = fields.Char(string="New Position", tracking=True)
    pai_currency_id = fields.Many2one(related='pai_employee_id.company_id.currency_id', string='Company Currency', readonly=True, tracking=True)
    pai_salary_increment = fields.Monetary('Salary Increment', currency_field="pai_currency_id", help="Employee's Salary Increment amount.", tracking=True)
    pai_pdf_date = fields.Date(string="PDF Date", tracking=True)
    pai_start_date = fields.Date(string="Start From", tracking=True)

    # probation confirmation letter with salary
    pcl_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    pcl_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    pcl_letter_date = fields.Date(string="Letter Date", tracking=True)
    pcl_effective_date = fields.Date(string="Effective Date", tracking=True)
    pcl_currency_id = fields.Many2one(related='pcl_employee_id.company_id.currency_id', string='Company Currency', readonly=True, tracking=True)
    pcl_basic_salary = fields.Monetary('Basic Salary', currency_field="pcl_currency_id", help="Employee's Basic Salary amount.", tracking=True)
    pcl_revised_salary = fields.Monetary('Revised Salary', currency_field="pcl_currency_id", help="Employee's Revised Salary amount.", tracking=True)

    # probation confirmation letter without salary
    pclws_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    pclws_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    pclws_letter_date = fields.Date(string="Letter Date", tracking=True)
    pclws_effective_date = fields.Date(string="Effective Date", tracking=True)

    # Promotion Letter
    prom_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title',tracking=True)
    prom_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    prom_letter_date = fields.Date(string="Letter Date", tracking=True)
    prom_position = fields.Char(string="New Designation", tracking=True)

    #Resignation Acceptance Letter
    ral_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title',tracking=True)
    ral_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    ral_letter_date = fields.Date(string="Letter Date", tracking=True)
    ral_resign_date = fields.Date(string="Resign Letter Date", tracking=True)
    ral_relieved_date = fields.Date(string="Resign Letter Date", tracking=True)

    # Deputaion Letter
    dl_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    dl_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    dl_letter_date = fields.Date(string="Letter Date", tracking=True)
    dl_from_date = fields.Date(string="From Date", tracking=True)
    dl_deputed_to = fields.Many2one('res.company', string='Deputed To', tracking=True)
    dl_designation = fields.Char(string='Designation', tracking=True)
    dl_deputed_salary = fields.Char(string='Deputed Salary', tracking=True)
    dl_accommodation_details = fields.Char(string='Accommodation Details', tracking=True)
    dl_law = fields.Selection([('kll', 'Kuwait Labour Law.'), ('ill', 'Indian Labour Law.')], 'Law',tracking=True)

    #salary Certification
    sc_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
    sc_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    sc_letter_date = fields.Date(string="Letter Date", tracking=True)
    sc_currency_id = fields.Many2one(related='sc_employee_id.company_id.currency_id', string='Company Currency', tracking=True)
    sc_monthly_salary = fields.Monetary('Basic Salary', currency_field="sc_currency_id", help="Employee's Monthly Salary amount.", tracking=True)

    # Vehicle Acknowledgement Form
    va_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title',tracking=True)
    va_employee_id = fields.Many2one('hr.employee', string="To Employee", tracking=True)
    va_letter_date = fields.Date(string="Letter Date", tracking=True)
    va_nationality = fields.Char(string="Nationality", tracking=True)
    va_vehicle_model = fields.Char(string="Vehicle Model", tracking=True)
    va_vehicle_number = fields.Char(string="Vehicle Number", tracking=True)


    # Notification of leave return
    date_resumed_work = fields.Date(string="Date of Resumed Work", tracking=True)
    date_of_departure = fields.Date(string="Date of Departure", tracking=True)
    date_of_arrival = fields.Date(string="Date of Arrival", tracking=True)
    nlr_status = fields.Selection([('early', 'Early'), ('on_time', 'On Time'), ('late', 'Late')], 'Return Status', tracking=True)
    nlr_days = fields.Char(string="Days", tracking=True)
    nlr_if_late = fields.Char(string="If Late", tracking=True)
    hr_nlr_status = fields.Selection([('early', 'Early'), ('on_time', 'On Time'), ('late', 'Late')], 'Return Status', tracking=True)
    hr_days = fields.Char(string="Days", tracking=True)
    hr_passport_returned = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Return Status', tracking=True)
    hr_remarks = fields.Char(string="Remarks", tracking=True)

    # Loan Request Form
    lrf_amount_request = fields.Monetary('Amount Requested', currency_field="lrf_currency_id", tracking=True)
    lrf_reason_for_request = fields.Char(string="Reason For Request", tracking=True)
    lrf_currency_id = fields.Many2one(related='employee_id.company_id.currency_id', string='Company Currency', readonly=True, tracking=True)
    lrf_basic_salary = fields.Monetary('Basic Salary', currency_field="lrf_currency_id", tracking=True)
    lrf_previous_loans = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Previous Loans', tracking=True)
    lrf_pending_loan_amount = fields.Monetary('Pending Loan Amount', currency_field="lrf_currency_id", tracking=True)
    lrf_eligible_loan_amount = fields.Monetary('Eligible Loan Amount', currency_field="lrf_currency_id", tracking=True)
    lrf_recommended_loan_amount = fields.Monetary('Recommended Loan Amount', currency_field="lrf_currency_id", tracking=True)
    lrf_loan_approved = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Loan Approved', tracking=True)
    lrf_no_of_installments = fields.Integer(string="No. of Installments", tracking=True)
    lrf_monthly_deduction_amount = fields.Monetary('Monthly Deduction Amount', currency_field="lrf_currency_id", tracking=True)
    lrf_finance_loan_approved = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Loan Approved', tracking=True)
    lrf_mgmt_loan_approved = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Loan Approved', tracking=True)

    # No Objection Letter to Embassy
    nol_form_date = fields.Date(string="Form Date", tracking=True)
    nol_the_embassy_of = fields.Char(string="The embassy of", tracking=True)
    nol_nationality_id = fields.Many2one("res.country", string="Nationality", tracking=True)
    nol_applicant_name = fields.Char(string="Name of the applicant", tracking=True)
    nol_passport_number = fields.Char(string="Passport Number", tracking=True)
    nol_emp_part = fields.Char(string="Employed / Partner", tracking=True)
    nol_company_name = fields.Char(string="Company Name", tracking=True)
    nol_designation = fields.Char(string="Designation", tracking=True)
    nol_since = fields.Date(string="Since", tracking=True)
    nol_salary_amount = fields.Char(string="Salary Amount", tracking=True)
    nol_start_date = fields.Date(string="Start Date", tracking=True)
    nol_end_date = fields.Date(string="End Date", tracking=True)

    # Internship Certificate
    ic_form_date = fields.Date(string="Form Date", tracking=True)
    ic_student_name = fields.Char(string="Student Name", tracking=True)
    ic_clg_university = fields.Char(string="College / University", tracking=True)
    ic_company_id = fields.Many2one('res.company', string='Company')
    ic_department_id = fields.Many2one('hr.department', string="Department")
    ic_start_date = fields.Date(string="Start Date", tracking=True)
    ic_end_date = fields.Date(string="End Date", tracking=True)
    ic_guidance_of = fields.Char(string="Guidance Of", tracking=True)

    # Tablet Acknowledge form
    taf_made_by = fields.Date(string="Form Date", tracking=True)
    taf_model_type = fields.Char(string="Model / Type", tracking=True)
    taf_serial_no = fields.Char(string="Serial No.", tracking=True)
    taf_color = fields.Char(string="Color", tracking=True)
    taf_charger = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Charger', tracking=True)
    taf_keyboard = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Keyboard', tracking=True)
    taf_mouse = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Mouse', tracking=True)
    taf_laptop_bag = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Laptop Bag', tracking=True)
    taf_date_of = fields.Date(string="Date of", tracking=True)
    taf_title = fields.Selection([('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')], 'Title', tracking=True)
