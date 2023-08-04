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



class UserEmployeeContract(models.TransientModel):
    _name = 'user.employee.contracts.import'
    _description = 'User Employee Contract Import'

    upload_file = fields.Binary(string="Upload File")


    def button_submit(self):
        print("Running")
        data = base64.b64decode(self.upload_file)
        with open('/tmp/' + 'Sheet1', 'wb') as file:
            file.write(data)
        xl_workbook = xlrd.open_workbook(file.name)
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        # Number of columns
        num_cols = xl_sheet.ncols
        headers = []
        header_fields = []
        for col_idx in range(0, num_cols):
            cell_obj = xl_sheet.cell(0, col_idx)
            cell_value = cell_obj.value.strip()
            headers.append(cell_value)
            if cell_value == 'User Name':
                header_fields.append('name')
            elif cell_value == 'Login':
                header_fields.append('login')
            elif cell_value == 'Company Name':
                header_fields.append('company_id')
        print("[[[[[[[[[[[[",header_fields)
        import_data = []
        for row_idx in range(1, xl_sheet.nrows):  # Iterate through rows
            row_dict = {}
            for col_idx in range(0, num_cols):  # Iterate through columns
                cell_obj = xl_sheet.cell(row_idx, col_idx)
                row_dict[header_fields[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        for data in import_data:
            if not data['name']:
                raise ValidationError(_('please check your data list "name" missed some record'))
            if not data['login']:
                raise ValidationError(_('please check your data list "login" missed some record'))
            if not data['company_id']:
                raise ValidationError(_('please check your data list "Company Name" missed some record'))

        for row in import_data:
            company = self.env['res.company']
            comp = company.search([('name', '=', row['company_id'].strip())], limit=1)
            if not comp:
                comp = company.create({'name': row['company_id'].strip()})

            user_vals = {
                'name': row['name'],
                'login': row['login'],
                'company_id': comp.id,

            }
            user_id = self.env['res.users'].create(user_vals)
            print("::::::::::::::",user_id)

            employee_vals = {
                'firstname': row['name'],
                'lastname': row['name'],
                'company_id': comp.id,
                'user_id': user_id.id,

            }

            employee_id = self.env['hr.employee'].create(employee_vals)
            contract_history = self.env['hr.contract.history'].search([('employee_id', '=', employee_id.id)])
            print("iiiiiiiiiiiii",contract_history)

            contract_vals = {
                'name': row['name'],
                # 'hr_responsible_id': 869,
                # 'struct_id': 4,
                'wage': 0.00,
                'employee_id': employee_id.id,

            }

            contract_id = contract_history
            con = contract_id.contract_ids.create(contract_vals)
            print("11111111111111111111111111",con)



                
