from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import base64
import io


class JobDescription(models.Model):
    _name = 'job.description'
    _description = 'Job Description'
    _rec_name = 'skill_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', string="Skill", required=True)
    skill_level_id = fields.Many2one('hr.skill.level', string="Skill Level", required=True)
    skill_type_id = fields.Many2one('hr.skill.type', string="Skill Type", required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')


