from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round

import base64
from datetime import datetime, date,time, timedelta
from pytz import utc
import calendar
from pytz import timezone
from collections import defaultdict
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
import time


class EmployeeLeaveAllocation(models.Model):
    _name = 'employee.leave.allocation'
    _description = 'Leave Allocation'

    name = fields.Char(string='Name', required=True)
    leave_type_id = fields.Many2one('hr.leave.type',  required=True, string='Leave Type')
    company_id = fields.Many2one('res.company',  readonly=True, string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, readonly=True)
    date_from = fields.Date(string='Date From', required=True, help="Start date", default=time.strftime('%Y-01-01'))
    date_to = fields.Date(string='Date To', required=True, help="End date", default=time.strftime('%Y-12-31'))
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("allocated", "Allocated"),
        ], string="Status", default="draft", required=True
    )

    def unlink(self):
        for rec in self:
            if rec.state == 'allocated':
                raise ValidationError(_("Cannot delete record that not in state 'Allocated'"))
        return super(EmployeeLeaveAllocation, self).unlink()




    def leave_allocation(self):
        employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id),
                                                    # ('company_id', '>=', self.date_from),
                                                    # ('company_id', '<=', self.date_to)
                                                    ])
        # print("KKKKKKKKKKKKKKKK",len(employees))
        if employees:
            for employee in employees:
               if employee.date_of_joining:
                   date = employee.date_of_joining
                   period_date = employee.probation_period
                   after_period_date = (date + relativedelta(days=period_date+1)).strftime('%Y-%m-%d'),
                   year_end_date = time.strftime('%Y-12-31')
                   year_end_date = datetime.strptime(year_end_date, '%Y-%m-%d').date()
                   after_period_date = datetime.strptime(after_period_date[0], '%Y-%m-%d').date()
                   # print("!!!!!!!!!!1111111111",date, period_date, after_period_date, year_end_date, employee.name)
                   sl = relativedelta(year_end_date, after_period_date)
                   print("1111111111", year_end_date, date, employee.name)
                   cl = relativedelta(year_end_date, date)
                   print(";;;;;;;;;",cl.years * 12 + cl.months, cl.days, employee.name)
                   sl_month_diff = sl.years * 12 + sl.months
                   cl_month_diff = cl.years * 12 + cl.months
                   # if cl_month_diff < 12 and cl.days > 15:
                   if employee.state == 'employment':
                       if not self.leave_type_id.code == 'EARNEDLEAVE' and self.leave_type_id.code == 'SICKLEAVE':
                           allocation = self.env['hr.leave.allocation'].create({
                                'name': self.name,
                                'holiday_status_id': self.leave_type_id.id,
                                'number_of_days': 12 if sl_month_diff > 12 else sl_month_diff + 1 if sl_month_diff < 12 and sl.days > 15 else sl_month_diff,
                                'employee_id': employee.id,
                                'employee_ids': employee.ids,
                                'state': 'confirm',
                                'date_from': after_period_date if self.date_from < after_period_date else self.date_from,
                                'date_to': self.date_to,
                           })
                           self.write({'state': 'allocated'})
                   if not self.leave_type_id.code == 'EARNEDLEAVE' and self.leave_type_id.code == 'CASUALLEAVE':
                       attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
                       print("len",len(attendance))
                       if len(attendance) > 15:
                           allocation = self.env['hr.leave.allocation'].create({
                                'name': self.name,
                                'holiday_status_id': self.leave_type_id.id,
                                'number_of_days': 12 if cl_month_diff > 12 else cl_month_diff + 1 if cl_month_diff < 12 and cl.days > 15 else cl_month_diff,
                                'employee_id': employee.id,
                                'employee_ids': employee.ids,
                                'state': 'confirm',
                                'date_from': date if self.date_from < date else self.date_from,
                                'date_to': self.date_to,
                           })
                       self.write({'state': 'allocated'})
                   if self.leave_type_id.code == 'EARNEDLEAVE':
                       if month_diff > 12:
                           allocation = self.env['hr.leave.allocation'].create({
                               'name': self.name,
                               'holiday_status_id': self.leave_type_id.id,
                               'number_of_days': 24,
                               'employee_id': employee.id,
                               'employee_ids': employee.ids,
                               'state': 'confirm',
                               'date_from': self.date_from,
                               'date_to': self.date_to,
                           })
                           self.write({'state': 'allocated'})





