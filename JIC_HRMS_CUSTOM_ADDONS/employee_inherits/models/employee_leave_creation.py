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


class EmployeeLeaveCreation(models.Model):
    _name = 'employee.leave.creation'
    _description = 'Leave Creation'

    name = fields.Many2one('hr.employee',  required=True, string='Created Employees Name')
    employee_ids = fields.Many2many('hr.employee', required=True, string='Employees')
    date_from = fields.Date(string='Date From', required=True, help="Start date",
                            default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=-1, day=26)).date()))
    date_to = fields.Date(string='Date To', required=True, help="End date",
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(day=25)).date()))


    def leave_creation(self):
        if self.employee_ids:
            for employee in self.employee_ids:
                date_from = self.date_from
                date_to = self.date_to
                attendance_id = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                  ('check_in', '>=', date_from),
                                                                  ('check_in', '<=', date_to)])
                leaves_id = self.env['hr.leave'].search([('employee_ids', 'in', employee.id),
                                                         ('request_date_from', '>=', date_from),
                                                         ('request_date_to', '<=', date_to),
                                                         ('state', '=', 'validate')])
                leaves_type = self.env['hr.leave.type'].search(
                    [('company_id', '=', employee.company_id.id), ('code', '=', 'UNPAID')])
                leaves_type_half = self.env['hr.leave.type'].search(
                    [('company_id', '=', employee.company_id.id), ('code', '=', 'UNPAIDHALF')])
                payroll_date = []
                attendance_date = []
                leaves = []
                second_half_absent = []
                leaves_pm = []
                lop = []
                lop_absent_pm = []
                leaves_am = []
                calendar = self.env['resource.calendar'].search([('id', '=', employee.resource_calendar_id.id)])

                for d in rrule(DAILY, dtstart=date_from, until=date_to):
                    payroll_day_name = d.strftime('%A')
                    if payroll_day_name != 'Sunday':
                        payroll_date.append(d.strftime("%Y-%m-%d"))
                for att in attendance_id:
                    if att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        attendance_date.append(date)
                        print("fullll day absent", att.id, date, att.first_half_status, att.second_half_status,employee.id)
                    if not att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        print("second halffffffffffffff", att.id, date, att.first_half_status, att.second_half_status,employee.id)
                        date = att.check_in.strftime("%Y-%m-%d")
                        second_half_absent.append(date)
                    if att.first_half_status == 'lop' and att.second_half_status == 'present' or att.first_half_status == 'lop' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        print("LLLLLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOOOOOOOOOPPPPPPPP", att.id, date, att.first_half_status,att.second_half_status, employee.id)
                        lop.append(date)
                    # if att.first_half_status == 'lop' and att.second_half_status == 'absent':
                    #     date = att.check_in.strftime("%Y-%m-%d")
                    #     lop_absent_am.append(date)
                for leave in leaves_id:
                    if leave.request_date_from_period == 'pm':
                        leave_date_to = leave.request_date_from.strftime("%Y-%m-%d")
                        leaves_pm.append(leave_date_to)
                    elif leave.request_date_from_period == 'am':
                        leave_date_to = leave.request_date_from.strftime("%Y-%m-%d")
                        leaves_am.append(leave_date_to)
                    else:
                        leave_date_from = leave.request_date_from.strftime("%Y-%m-%d")
                        leave_date_to = leave.request_date_to.strftime("%Y-%m-%d")
                        leaves.append(leave_date_from)
                        leaves.append(leave_date_to)
                print("LLLLLLLLLLLLLLLLLLL,second half", second_half_absent, employee.id)
                print("LLLLLLLLLLLLLLLLLLL,op", lop, employee.id)
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            time = datetime.combine(date, datetime.min.time())
                            print("yyyyyyyy", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type.id,
                                    'request_date_from': time + timedelta(hours=6),
                                    'date_from': time + timedelta(hours=6),
                                    'date_to': time + timedelta(hours=15),
                                    'request_date_to': time + timedelta(hours=15),
                                    'number_of_days': 1,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()
                    if pd in second_half_absent:
                        print("qqqqqqqqqqqqqq", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type_half.id,
                                    'request_unit_half': True,
                                    'request_date_from_period': 'pm',
                                    'request_date_from': date,
                                    'date_from': date,
                                    'date_to': date,
                                    'request_date_to': date,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()

                    if pd in lop:
                        print("lopppppppppppppppppppppppppppp", leaves_am, employee.id)
                        if pd not in leaves_am:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            print("===================", employee.id)
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type_half.id,
                                    'request_unit_half': True,
                                    'request_date_from_period': 'am',
                                    'request_date_from': date,
                                    'date_from': date,
                                    'date_to': date,
                                    'request_date_to': date,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()

    def leave_creation_cron(self):
        employee_ids = self.env['hr.employee'].search([])
        print("1111111111111111111", employee_ids)
        if employee_ids:
            for employee in employee_ids:
                from_date = fields.Date.to_string((datetime.now() + relativedelta(months=-1, day=26)).date())
                to_date = fields.Date.to_string((datetime.now() + relativedelta(day=25)).date())
                date_from = datetime.strptime(from_date, '%Y-%m-%d').date()
                date_to = datetime.strptime(to_date, '%Y-%m-%d').date()
                attendance_id = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                  ('check_in', '>=', date_from),
                                                                  ('check_in', '<=', date_to)])
                leaves_id = self.env['hr.leave'].search([('employee_ids', 'in', employee.id),
                                                         ('request_date_from', '>=', date_from),
                                                         ('request_date_to', '<=', date_to),
                                                         ('state', '=', 'validate')])
                leaves_type = self.env['hr.leave.type'].search([('company_id', '=', employee.company_id.id), ('code', '=', 'UNPAID')])
                leaves_type_half = self.env['hr.leave.type'].search([('company_id', '=', employee.company_id.id), ('code', '=', 'UNPAIDHALF')])
                payroll_date = []
                attendance_date = []
                leaves = []
                second_half_absent = []
                leaves_pm = []
                lop = []
                lop_absent_pm = []
                leaves_am = []
                calendar = self.env['resource.calendar'].search([('id', '=', employee.resource_calendar_id.id)])

                for d in rrule(DAILY, dtstart=date_from, until=date_to):
                    payroll_day_name = d.strftime('%A')
                    if payroll_day_name != 'Sunday':
                        payroll_date.append(d.strftime("%Y-%m-%d"))
                for att in attendance_id:
                    if att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        attendance_date.append(date)
                        print("fullll day absent", att.id, date,att.first_half_status, att.second_half_status, employee.id)
                    if not att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        print("second halffffffffffffff", att.id, date, att.first_half_status, att.second_half_status, employee.id)
                        date = att.check_in.strftime("%Y-%m-%d")
                        second_half_absent.append(date)
                    if att.first_half_status == 'lop' and att.second_half_status == 'present' or att.first_half_status == 'lop' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        print("LLLLLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOOOOOOOOOPPPPPPPP",att.id, date, att.first_half_status,att.second_half_status, employee.id)
                        lop.append(date)
                    # if att.first_half_status == 'lop' and att.second_half_status == 'absent':
                    #     date = att.check_in.strftime("%Y-%m-%d")
                    #     lop_absent_am.append(date)
                for leave in leaves_id:
                    if leave.request_date_from_period == 'pm':
                        leave_date_to = leave.request_date_from.strftime("%Y-%m-%d")
                        leaves_pm.append(leave_date_to)
                    elif leave.request_date_from_period == 'am':
                        leave_date_to = leave.request_date_from.strftime("%Y-%m-%d")
                        leaves_am.append(leave_date_to)
                    else:
                        leave_date_from = leave.request_date_from.strftime("%Y-%m-%d")
                        leave_date_to = leave.request_date_to.strftime("%Y-%m-%d")
                        leaves.append(leave_date_from)
                        leaves.append(leave_date_to)
                print("LLLLLLLLLLLLLLLLLLL,second half", second_half_absent, employee.id)
                print("LLLLLLLLLLLLLLLLLLL,op", lop, employee.id)
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            time = datetime.combine(date, datetime.min.time())
                            print("yyyyyyyy", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type.id,
                                    'request_date_from': time + timedelta(hours=6),
                                    'date_from': time + timedelta(hours=6),
                                    'date_to': time + timedelta(hours=15),
                                    'request_date_to': time + timedelta(hours=15),
                                    'number_of_days': 1,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()
                    if pd in second_half_absent:
                        print("qqqqqqqqqqqqqq", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type_half.id,
                                    'request_unit_half': True,
                                    'request_date_from_period': 'pm',
                                    'request_date_from': date,
                                    'date_from': date,
                                    'date_to': date,
                                    'request_date_to': date,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()

                    if pd in lop:
                        print("lopppppppppppppppppppppppppppp",leaves_am, employee.id)
                        if pd not in leaves_am:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            print("===================", employee.id)
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Attendance',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type_half.id,
                                    'request_unit_half': True,
                                    'request_date_from_period': 'am',
                                    'request_date_from': date,
                                    'date_from': date,
                                    'date_to': date,
                                    'request_date_to': date,
                                    'state': 'draft',

                                })
                                leave._compute_date_from_to()
                                leave.action_confirm()
                                leave.action_approve()
                    # elif pd in lop_absent_am:
                    #     print("qqqqqqqqqqqqqq")
                    #     if pd not in leaves_pm:
                    #         date = datetime.strptime(pd, '%Y-%m-%d').date()
                    #         # time = datetime.combine(date, datetime.min.time())
                    #         print("===================")
                    #         if employee:
                    #             leave = self.env['hr.leave'].create({
                    #                 'employee_id': employee.id,
                    #                 'name': 'Attendance',
                    #                 'holiday_type': 'employee',
                    #                 'mode_company_id': employee.company_id.id,
                    #                 'holiday_status_id': leaves_type_half.id,
                    #                 'request_unit_half': True,
                    #                 'request_date_from_period': 'am',
                    #                 'request_date_from': date,
                    #                 'date_from': date,
                    #                 'date_to': date,
                    #                 'request_date_to': date,
                    #                 'state': 'draft',
                    #
                    #             })
                    #             leave._compute_date_from_to()
                    #             leave.action_confirm()
                    #             leave.action_approve()
