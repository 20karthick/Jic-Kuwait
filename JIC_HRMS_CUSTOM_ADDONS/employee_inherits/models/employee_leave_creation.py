from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round

import base64
from datetime import datetime, date,time, timedelta
from pytz import utc
import calendar as cl
from pytz import timezone
from collections import defaultdict
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
import time
from odoo.tools import date_utils
from itertools import groupby
from datetime import datetime
from operator import itemgetter
# import pandas as pds

class WeekOff(models.Model):
    _name = "week.off"
    _description = "Resource Working Time"

    company_ids = fields.Many2many('res.company')
    leave_count = fields.Integer('Leave count', size=1)

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
                week_off_master = self.env['week.off'].search(
                    [('company_ids', 'in', employee.company_id.id)])

                payroll_date = []
                attendance_date = []
                leaves = []
                second_half_absent = []
                first_half_absent = []
                leaves_pm = []
                lop = []
                lop_absent_pm = []
                leaves_am = []
                week_days_string = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                week_day_list = []
                for week_days in employee.resource_calendar_id.attendance_ids:
                    week_day_list.append(dict(week_days._fields['dayofweek'].selection).get(week_days.dayofweek))
                wds_list = []
                for wds in week_days_string:
                    if wds not in [*set(week_day_list)]:
                        wds_list.append(wds)
                for d in rrule(DAILY, dtstart=date_from, until=date_to):
                    payroll_day_name = d.strftime('%A')
                    if payroll_day_name not in wds_list:
                        payroll_date.append(d.strftime("%Y-%m-%d"))
                for att in attendance_id:
                    if att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        attendance_date.append(date)
                    if not att.first_half_status in ['present', 'absent', 'sick_leave', 'casual_leave'] and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        second_half_absent.append(date)
                    if att.first_half_status == 'lop' and att.second_half_status in ['present', 'absent', 'sick_leave', 'casual_leave']:
                        date = att.check_in.strftime("%Y-%m-%d")
                        lop.append(date)
                    if att.first_half_status == 'absent' and att.second_half_status in ['present', 'lop', 'sick_leave', 'casual_leave']:
                        date = att.check_in.strftime("%Y-%m-%d")
                        first_half_absent.append(date)
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

        # ooooooooooo
                date_list = []
                leave_date_list = []
                for p_date in payroll_date:
                    if p_date in attendance_date:
                        if p_date not in leaves:
                            date = datetime.strptime(p_date, '%Y-%m-%d').date()
                            time = datetime.combine(date, datetime.min.time())
                            date_list.append(date)
                date_from_l = min(date_list)
                date_to_l = max(date_list)
                delta = date_to_l - date_from_l
                for i in range(delta.days + 1):
                    day = date_from + timedelta(days=i)
                    leave_date_list.append(day)

                week_off_days = []
                for rec in leave_date_list:
                    if rec.strftime('%A') in wds_list:
                        week_off_days.append(rec)

                emp_present_days = []
                for att in attendance_id:
                    if att.first_half_status in ['present', 'lop', 'sick_leave', 'casual_leave'] or att.second_half_status in ['present', 'lop', 'sick_leave', 'casual_leave']:
                        p_date = att.check_in.strftime("%Y-%m-%d")
                        date = datetime.strptime(p_date, '%Y-%m-%d').date()
                        emp_present_days.append(date)
                full_day_leave = []
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            full_day_leave.append(date)

                # new_list = sorted(list(set(leave_date_list).difference(full_day_leave)))
                present_sorted = sorted(emp_present_days)
                print("present$$$$$$$$$$$$$$$$$$$$$", present_sorted)
                # print("leave*********************", full_day_leave)
                # print("week_off#####################", week_off_days)

                sandwich = []
                sandwich_combine = []

                if week_off_master:
                    leave_list = list()
                    leave_size = week_off_master.leave_count
                    for i in range(0, len(week_off_days), leave_size):
                        leave_list.append(week_off_days[i:i + leave_size])

                    for wod in leave_list:
                        min_wod = min(wod)
                        max_wod = max(wod)
                        off_minus = min_wod + relativedelta(days=-1)
                        off_plus = max_wod + relativedelta(days=1)
                        if off_minus and off_plus in full_day_leave:
                            join = str(off_minus) + ',' + str(off_plus)
                            list_date = join.split(',')
                            sandwich.append(list_date)
                        #     print("111111111", off_minus, off_plus)
                        # else:
                        #     print("222222222222", off_minus, off_plus)
                for sand in sandwich:
                    for s in sand:
                        date = datetime.strptime(s, '%Y-%m-%d').date()
                        sandwich_combine.append(date)

                all_leave = []
                leave_create = []
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            all_leave.append(date)
                for al in all_leave:
                    if al not in sandwich_combine:
                        leave_create.append(al)


                if sandwich:
                    for sw in sandwich:
                        sw_from_date = min(sw)
                        sw_to_date = max(sw)
                        from_date_format = datetime.strptime(sw_from_date, '%Y-%m-%d').date()
                        to_date_format = datetime.strptime(sw_to_date, '%Y-%m-%d').date()
                        add_from_time = datetime.combine(from_date_format, datetime.min.time())
                        add_to_time = datetime.combine(to_date_format, datetime.min.time())
                        if from_date_format not in present_sorted and to_date_format not in present_sorted:
                            if employee:
                                print("sandwich")
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Sandwich',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type.id,
                                    'request_date_from': add_from_time + timedelta(hours=6),
                                    'date_from': add_from_time + timedelta(hours=6),
                                    'date_to': add_to_time + timedelta(hours=15),
                                    'request_date_to': add_to_time + timedelta(hours=15),
                                    # 'number_of_days': 3,
                                    'state': 'draft',
                                    'sandwich_rule': True,

                                })
                                leave._compute_date_from_to()
                                leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            for lc in leave_create:
                                if lc == date:
                                    time = datetime.combine(date, datetime.min.time())
                                    if employee:
                                        leave = self.env['hr.leave'].create({
                                            'employee_id': employee.id,
                                            'name': 'Full day Absent',
                                            'holiday_type': 'employee',
                                            'mode_company_id': employee.company_id.id,
                                            'holiday_status_id': leaves_type.id,
                                            'request_date_from': time + timedelta(hours=6),
                                            'date_from': time + timedelta(hours=6),
                                            'date_to': time + timedelta(hours=15),
                                            'request_date_to': time + timedelta(hours=15),
                                            # 'number_of_days': 1,
                                            'state': 'draft',

                                        })
                                        leave._compute_date_from_to()
                                        leave.check_leave_type()
                                        leave.action_confirm()
                                        leave.action_approve()
                    if pd in second_half_absent:
                        print("second_half_absent", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Second half Absent',
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
                                    'request_unit_half': True,
                                    # 'number_of_days': 0.50,

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()
                    if pd in first_half_absent:
                        print("first_half_absent", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'First Half Absent',
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
                                    'request_unit_half': True,
                                    # 'number_of_days': 0.50,

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
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
                                    'name': 'First Half Lop',
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
                                    'request_unit_half': True,
                                    # 'number_of_days': 0.50,

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()


            # kkkkkkkk
    def leave_creation_cron(self):
        employee_ids = self.env['hr.employee'].search([])
        print("1111111111111111111", employee_ids)
        if employee_ids:
            for employee in employee_ids:
                # from_date = fields.Date.to_string((datetime.now() + relativedelta(months=-1, day=26)).date())
                # to_date = fields.Date.to_string((datetime.now() + relativedelta(day=25)).date())
                from_date = '2023-07-26'
                to_date = '2023-08-25'
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
                week_off_master = self.env['week.off'].search(
                    [('company_ids', 'in', employee.company_id.id)])
                payroll_date = []
                attendance_date = []
                leaves = []
                second_half_absent = []
                first_half_absent = []
                leaves_pm = []
                lop = []
                lop_absent_pm = []
                leaves_am = []
                calendar = self.env['resource.calendar'].search([('id', '=', employee.resource_calendar_id.id)])
                week_days_string = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                week_day_list = []
                for week_days in employee.resource_calendar_id.attendance_ids:
                    week_day_list.append(dict(week_days._fields['dayofweek'].selection).get(week_days.dayofweek))
                wds_list = []
                for wds in week_days_string:
                    if wds not in [*set(week_day_list)]:
                        wds_list.append(wds)

                for d in rrule(DAILY, dtstart=date_from, until=date_to):
                    payroll_day_name = d.strftime('%A')
                    if payroll_day_name not in wds_list:
                        payroll_date.append(d.strftime("%Y-%m-%d"))
                for att in attendance_id:
                    if att.first_half_status == 'absent' and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        attendance_date.append(date)
                    if not att.first_half_status in ['present', 'absent', 'sick_leave','casual_leave'] and att.second_half_status == 'absent':
                        date = att.check_in.strftime("%Y-%m-%d")
                        second_half_absent.append(date)
                    if att.first_half_status == 'lop' and att.second_half_status in ['present', 'absent', 'sick_leave','casual_leave']:
                        date = att.check_in.strftime("%Y-%m-%d")
                        lop.append(date)
                    if att.first_half_status == 'absent' and att.second_half_status in ['present', 'lop', 'sick_leave','casual_leave']:
                        date = att.check_in.strftime("%Y-%m-%d")
                        first_half_absent.append(date)
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
                print("LLLLLLLLLLLLLLLLLLL,op", payroll_date, attendance_date, leaves)
                date_list = []
                leave_date_list = []
                for p_date in payroll_date:
                    if p_date in attendance_date:
                        if p_date not in leaves:
                            date = datetime.strptime(p_date, '%Y-%m-%d').date()
                            time = datetime.combine(date, datetime.min.time())
                            date_list.append(date)
                print("<<<<<<<<<<<<<<<<<<LLLLLLLLLLLLLLLLLLL>>>>>>>>>>>>>>>>>>", date_list)
                if date_list:
                    date_from_l = min(date_list)
                    date_to_l = max(date_list)
                    delta = date_to_l - date_from_l
                    for i in range(delta.days + 1):
                        day = date_from + timedelta(days=i)
                        leave_date_list.append(day)

                week_off_days = []
                for rec in leave_date_list:
                    if rec.strftime('%A') in wds_list:
                        week_off_days.append(rec)

                emp_present_days = []
                for att in attendance_id:
                    if att.first_half_status in ['present', 'lop', 'sick_leave', 'casual_leave'] or att.second_half_status in ['present', 'lop', 'sick_leave', 'casual_leave']:
                        p_date = att.check_in.strftime("%Y-%m-%d")
                        date = datetime.strptime(p_date, '%Y-%m-%d').date()
                        emp_present_days.append(date)
                full_day_leave = []
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            full_day_leave.append(date)

                # new_list = sorted(list(set(leave_date_list).difference(full_day_leave)))
                present_sorted = sorted(emp_present_days)
                # print("present$$$$$$$$$$$$$$$$$$$$$", present_sorted)
                # print("leave*********************", full_day_leave)
                # print("week_off#####################", week_off_days)

                sandwich = []
                sandwich_combine = []

                if week_off_master:
                    leave_list = list()
                    leave_size = week_off_master.leave_count
                    for i in range(0, len(week_off_days), leave_size):
                        leave_list.append(week_off_days[i:i + leave_size])

                    for wod in leave_list:
                        min_wod = min(wod)
                        max_wod = max(wod)
                        off_minus = min_wod + relativedelta(days=-1)
                        off_plus = max_wod + relativedelta(days=1)
                        if off_minus and off_plus in full_day_leave:
                            join = str(off_minus) + ',' + str(off_plus)
                            list_date = join.split(',')
                            sandwich.append(list_date)
                        #     print("111111111", off_minus, off_plus)
                        # else:
                        #     print("222222222222", off_minus, off_plus)
                for sand in sandwich:
                    for s in sand:
                        date = datetime.strptime(s, '%Y-%m-%d').date()
                        sandwich_combine.append(date)

                all_leave = []
                leave_create = []
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            all_leave.append(date)
                for al in all_leave:
                    if al not in sandwich_combine:
                        leave_create.append(al)

                if sandwich:
                    for sw in sandwich:
                        sw_from_date = min(sw)
                        sw_to_date = max(sw)
                        from_date_format = datetime.strptime(sw_from_date, '%Y-%m-%d').date()
                        to_date_format = datetime.strptime(sw_to_date, '%Y-%m-%d').date()
                        add_from_time = datetime.combine(from_date_format, datetime.min.time())
                        add_to_time = datetime.combine(to_date_format, datetime.min.time())
                        if from_date_format not in present_sorted and to_date_format not in present_sorted:
                            if employee:
                                print("sandwich")
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Sandwich',
                                    'holiday_type': 'employee',
                                    'mode_company_id': employee.company_id.id,
                                    'holiday_status_id': leaves_type.id,
                                    'request_date_from': add_from_time + timedelta(hours=6),
                                    'date_from': add_from_time + timedelta(hours=6),
                                    'date_to': add_to_time + timedelta(hours=15),
                                    'request_date_to': add_to_time + timedelta(hours=15),
                                    # 'number_of_days': 3,
                                    'state': 'draft',
                                    'sandwich_rule': True,

                                })
                                leave._compute_date_from_to()
                                leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()
                for pd in payroll_date:
                    if pd in attendance_date:
                        if pd not in leaves:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            for lc in leave_create:
                                if lc == date:
                                    time = datetime.combine(date, datetime.min.time())
                                    print("yyyyyyyy", type(date), date, time + timedelta(hours=6))
                                    if employee:
                                        leave = self.env['hr.leave'].create({
                                            'employee_id': employee.id,
                                            'name': 'Full Day Leave',
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
                                        leave.check_leave_type()
                                        leave.action_confirm()
                                        leave.action_approve()
                    if pd in second_half_absent:
                        print("second_half_absent", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'Second Half Absent',
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
                                    'number_of_days': 0.50

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()
                    if pd in first_half_absent:
                        print("first_half_absent", employee.id)
                        if pd not in leaves_pm:
                            date = datetime.strptime(pd, '%Y-%m-%d').date()
                            # time = datetime.combine(date, datetime.min.time())
                            # print("===================", type(date), date, time + timedelta(hours=6))
                            if employee:
                                leave = self.env['hr.leave'].create({
                                    'employee_id': employee.id,
                                    'name': 'First Half Absent',
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
                                    'request_unit_half': True,
                                    # 'number_of_days': 0.50,

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
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
                                    'name': 'First Half Lop',
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
                                    'number_of_days': 0.50,

                                })
                                leave._compute_date_from_to()
                                # leave.check_leave_type()
                                leave.action_confirm()
                                leave.action_approve()

