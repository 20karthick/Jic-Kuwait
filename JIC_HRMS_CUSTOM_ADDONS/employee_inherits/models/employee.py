from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class HrContractInherits(models.Model):
    _inherit = 'hr.contract'

    misc_allowance = fields.Float(string="Misc.Allowance")
    variable_inc = fields.Float(string="Variable Inc")
    arrears = fields.Float(string="Arrears")
    other_earnings = fields.Float(string="Other Earnings")
    incentive = fields.Float(string="Incentive")
    gmi_release = fields.Float(string="GMI Release")


class ResumeLineInherit(models.Model):
    _inherit = 'hr.resume.line'

    resume = fields.Many2many('ir.attachment',  string="Resume Attachment", copy=False)


class ResUsersInheritsUserGroup(models.Model):
    _inherit = 'res.users'

    @api.model
    def user_group_access(self):

        active_id = self.env['res.users'].browse(self.env.context.get('active_ids'))
        for user in active_id:
            if not user.has_group('employee_inherits.employee_rbac'):
                user.write({'groups_id': [(4, self.env.ref('employee_inherits.employee_rbac').id)]})
            if not user.has_group('hr.group_hr_user'):
                user.write({'groups_id': [(4, self.env.ref('hr.group_hr_user').id)]})
        return
