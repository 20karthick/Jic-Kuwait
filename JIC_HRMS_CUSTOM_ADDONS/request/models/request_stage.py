from odoo import api, fields, models, tools, exceptions, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta, time



class RequestStage(models.Model):
    _name = 'request.stage'
    _order = "sequence, id desc"

    name = fields.Char(string="Stage Name", required=True)
    sequence = fields.Integer('Sequence', required=True)
    request_type = fields.Selection([('rt_rr', 'Residence Transfer/ Renewal Request'), ('cp', 'Change in Pay'),
                                     ('maf', 'Mobile Acknowledgment'), ('paf', 'Passport Acknowledgment'), ('prf', 'Passport Release'),
                                     ('saf', 'Salary Advance'), ('vhf', 'Vehicle Handover'),('el', 'Experience Letter'), ('laf', 'Laptop Acknowledge'),
                                     ('ecf', 'Employee Clearance'), ('mrf', 'Manpower Requisition'), ('pai', 'Promotion and Increment'),
                                     ('pcl', 'Probation Confirmation letter with Salary'), ('pclws', 'Probation Confirmation letter without Salary'),
                                     ('prom', 'Promotion Letter (without Salary)'), ('ral', 'Resignation Acceptance Letter'), ('dl', 'Deputation Letter'),
                                     ('sc', 'Salary Certificate'), ('va', 'Vehicle Acknowledgement'), ('nlr', 'Notification of Leave Return'),
                                     ], 'Request Type', required=True)
    start_stage = fields.Boolean(string="Start Stage")
    end_stage = fields.Boolean(string="End Stage")
    user_id = fields.Many2one("res.users", string='Stage Approval')
    company_id = fields.Many2one('res.company', string='Company', required=True)

    @api.onchange('start_stage', 'end_stage')
    def onchange_stages(self):
        if self.user_id:
            if not self.start_stage and self.end_stage or not self.end_stage and self.start_stage:
                self.user_id = False
            else:
                if self.start_stage and self.end_stage:
                    self.user_id = False
                    raise UserError(_("kindly Choose First Stage or End Stage only."))

    @api.onchange('user_id')
    def onchange_user(self):
        if not self.start_stage and self.end_stage or not self.end_stage and self.start_stage:
            raise UserError(_("Stage and user cannot be selected at the same time. Choose only one."))


