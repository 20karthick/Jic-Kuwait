from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import base64
import io


class JobDescription(models.Model):
    _name = 'job.description'
    _description = 'Job Description'
    _rec_name = 'job_title'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin',]
    _mail_post_access = 'read'

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', required=True,  string="Created By", default=_default_employee, ondelete='cascade')
    job_title = fields.Char(string="Job Title", required=True, tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, tracking=True)
    dds = fields.Many2one('hr.department', string="Division / Department / Section", ondelete='cascade', tracking=True)
    location = fields.Char(string="Location", tracking=True)
    type_of_employment = fields.Selection([('fulltime', 'Full-time'), ('freelancing', 'Freelancing'), ('gigworking', 'Gig Working')], default='fulltime', string="Type of Employment", tracking=True)
    to_approve = fields.Many2one('hr.employee', required=True, string="Approved by HR Manager", ondelete='cascade')
    department_head = fields.Many2one('hr.employee', required=True, string="Department Head", ondelete='cascade')
    report_to = fields.Char(string='Report To')
    job_summary = fields.Text(string="Job Summary", tracking=True)
    dr = fields.Text(string="Duties and Responsibilities", tracking=True)
    edu_work_skill = fields.Text(string="Education / Work Experience / Skill Requirements", tracking=True)
    int_ext_com = fields.Text(string="Internal and External Communications", tracking=True)
    phy_req = fields.Text(string="Physical Requirements", tracking=True)
    department_head_signature_date = fields.Datetime(string="Date", tracking=True)
    hr_manager_signature_date = fields.Datetime(string="Date", tracking=True)
    document = fields.Binary('Download PDF', help="Upload PDF", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr_manger', 'HR Manager'),
        ('dep_head', 'Department Head'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
    ], string='Status', store=True, default='draft', tracking=True, readonly=False)
    dig_sign_hr_manager = fields.Binary(string='Hr Signature')
    dig_sign_department_head = fields.Binary(string='Department Head Signature')
    # skill_id = fields.Many2one('hr.skill', string="Skill", required=True)
    # skill_level_id = fields.Many2one('hr.skill.level', string="Skill Level", required=True)
    # skill_type_id = fields.Many2one('hr.skill.type', string="Skill Type", required=True)
    # level_progress = fields.Integer(related='skill_level_id.level_progress')


    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("A record can only be deleted in draft state."))
        return super(EmployeeLeaveApplication, self).unlink()

    def action_submit(self):
        for rec in self:
            if self.env.user.employee_id == rec.employee_id:
                rec.state = 'hr_manger'
            else:
                raise ValidationError(_("You can't Submit this document, Only can Approve this 'Created By' user."))

        return True
    def action_hr_manger(self):
        for rec in self:
            print("ppppppppppp",rec.to_approve, self.env.user.employee_id)
            if self.env.user.employee_id == rec.to_approve:
                rec.state = 'dep_head'
            else:
                raise ValidationError(_("You can't Approve this document, Only can Approve this 'Approved by HR Manager' user."))
        return True
    def action_dep_head(self):
        for rec in self:
            if self.env.user.employee_id == rec.department_head:
                rec.state = 'approve'
            else:
                raise ValidationError(_("You can't Approve this document, Only can Approve this 'Department Head' user."))
        return True
    def action_refuse(self):
        for rec in self:
            if rec.state == 'hr_manger':
                if self.env.user.employee_id == rec.to_approve:
                    rec.state = 'refuse'
                else:
                    raise ValidationError(_("You can't Refuse this document, Only can Refuse this 'Approved by HR Manager' user."))
            if rec.state == 'dep_head':
                if self.env.user.employee_id == rec.department_head:
                    rec.state = 'refuse'
                else:
                    raise ValidationError(_("You can't Refuse this document, Only can Refuse this 'Department Head' user."))

        return True

    def write(self, vals):
        print("vals",vals)
        if 'dig_sign_department_head' in vals:
            self.message_post(body=_("Department head signature signed by %s.", self.env.user.employee_id.name))
        if 'dig_sign_hr_manager' in vals:
            self.message_post(body=_("Approved by HR Manager signature signed by %s.", self.env.user.employee_id.name))
        if 'document' in vals:
            self.message_post(body=_("Download PDF Edited by %s.", self.env.user.employee_id.name))
        return super(JobDescription, self).write(vals)

    def action_draft(self):
        for rec in self:
            if rec.state == 'hr_manger':
                if self.env.user.employee_id == rec.to_approve:
                    rec.state = 'draft'
                else:
                    raise ValidationError(_("You can't Draft this document, Only can Reset this 'Approved by HR Manager' user."))
            if rec.state == 'dep_head':
                if self.env.user.employee_id == rec.department_head:
                    rec.state = 'draft'
                else:
                    raise ValidationError(_("You can't Draft this document, Only can Reset this 'Department Head' user."))

        return True

class ResUsersInherits(models.Model):
    _inherit = 'res.users'

    @api.model
    def employee_creation(self):

        active_id = self.env['res.users'].browse(self.env.context.get('active_ids'))
        user = self.env['res.users'].search([])
        for rec in active_id:
            if self.env.company.id == rec.company_id.id:
                if rec.employee_count == 0:
                    rec.action_create_employee()
            else:
                raise ValidationError(
                    _("Please select the applicable company"))

        return
