from odoo import api, fields, models, tools, exceptions, _
from odoo.osv import expression
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
import base64
from io import BytesIO
import xlrd
from odoo.tools import format_datetime


class HrAttendanceInherits(models.Model):
    _inherit = 'hr.attendance'

    def attendance_sent_mail(self):
        for rec in self:
            if rec.employee_id.work_email:
                # emails = [stud.email if stud.email else '']
                emails = [str(rec.employee_id.work_email)]
                # today = fields.date.today()
                if emails:
                    mail_ser_ids = self.env['ir.mail_server'].sudo().search([])
                    print(":::::::::::::::::::::",mail_ser_ids)
                    from_id = mail_ser_ids[0].smtp_user

                    Mail = self.env['mail.mail']
                    body_html = "<p>Dear " + str(rec.employee_id.name) + "</p>"
                    body_html += "<p>Visitor Code: "  "</p>"
                    body_html += "<p>Appointment Date / Time: "  "</p>"
                    body_html += "<p>Person To Visit: ""</p>"
                    # body_html += "<p>Person To Visit " + "(" + str(self.visitor_appointment_date) + ") " + "is the Appointment date" + '"' + str(
                    #     rec.person_to_visit) + '"' + ". Kindly return or renew the same to avoid the Penalty.</p>"
                    body_html += "<p>Regards,""</p>"
                    body_html += "<p>" "</p>"
                    mail_values = {
                        'email_from': from_id,
                        'reply_to': from_id,
                        'subject': "Attendance Details",
                        # 'attachment_ids': ,
                        'body_html': body_html,
                        # 'notification': True,
                    }
                    # Mail send
                    for email_to in emails:
                        if email_to:
                            print(email_to, '*******************')
                            mail_values.update({'email_to': email_to})
                            mail = Mail.sudo().create(mail_values)
                            mail.sudo().send()
                            # if mail.state == 'sent':
                            #     self.mail_sent = True

                            # if self.mail_sent == True:
                            #     message_id = self.env['visitor.mail.wizard'].create(
                            #         {'message': _("Mail Sent successfully.")})
                            #     return {
                            #         'name': _('Successfull'),
                            #         'type': 'ir.actions.act_window',
                            #         'view_mode': 'form',
                            #         'res_model': 'visitor.mail.wizard',
                            #         # pass the id
                            #         'res_id': message_id.id,
                            #         'target': 'new'
                            #     }

