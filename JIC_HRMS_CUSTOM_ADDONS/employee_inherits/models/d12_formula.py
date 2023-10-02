from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import image_process
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import re


class DTwelveFormula(models.Model):
    _name = 'd.twelve.formula'
    _description = 'D12 Formula'

    name = fields.Char(string='Name')
    department_id = fields.Many2one('d.twelve.department', "Department", index=True)

    # @api.model
    # def search_panel_select_range(self, field_name, **kwargs):
    #     print("----------------------------------")
    #     if field_name == 'department_id':
    #         enable_counters = kwargs.get('enable_counters', False)
    #         fields = ['display_name', 'parent_department_id']
    #         available_folders = self.env['d.twelve.department'].search([])
    #         print(":::::::::::::::::::::::::", available_folders)
    #         folder_domain = expression.OR(
    #             [[('parent_department_id', 'parent_of', available_folders.ids)], [('id', 'in', available_folders.ids)]])
    #         # also fetches the ancestors of the available folders to display the complete folder tree for all available folders.
    #         DocumentFolder = self.env['d.twelve.department'].sudo().with_context(hierarchical_naming=False)
    #         records = DocumentFolder.search_read(folder_domain, fields)
    #
    #         domain_image = {}
    #         if enable_counters:
    #             model_domain = expression.AND([
    #                 kwargs.get('search_domain', []),
    #                 kwargs.get('category_domain', []),
    #                 kwargs.get('filter_domain', []),
    #                 [(field_name, '!=', False)]
    #             ])
    #             domain_image = self._search_panel_domain_image(field_name, model_domain, enable_counters)
    #
    #         values_range = OrderedDict()
    #         for record in records:
    #             record_id = record['id']
    #             if enable_counters:
    #                 image_element = domain_image.get(record_id)
    #                 record['__count'] = image_element['__count'] if image_element else 0
    #             value = record['parent_department_id']
    #             record['parent_department_id'] = value and value[0]
    #             values_range[record_id] = record
    #
    #         if enable_counters:
    #             self._search_panel_global_counters(values_range, 'parent_department_id')
    #
    #         return {
    #             'parent_field': 'parent_folder_id',
    #             'values': list(values_range.values()),
    #         }
    #
    #     return super(DTwelveFormula, self).search_panel_select_range(field_name)
    #
    # @api.model
    # def search_panel_select_multi_range(self, field_name, **kwargs):
    #     search_domain = kwargs.get('search_domain', [])
    #     print("fffffffffffff", search_domain)
    #     category_domain = kwargs.get('category_domain', [])
    #     filter_domain = kwargs.get('filter_domain', [])
    #
    #     if field_name == 'tag_ids':
    #         folder_id = category_domain[0][2] if len(category_domain) else False
    #         print("::::::::::::::;", folder_id)
    #         if folder_id:
    #             domain = expression.AND([
    #                 search_domain, category_domain, filter_domain,
    #                 [(field_name, '!=', False)],
    #             ])
    #             return {'values': self._get_processed_tags(domain, folder_id)}
    #         else:
    #             return {'values': []}
    #
    #     elif field_name == 'res_model':
    #         domain = expression.AND([search_domain, category_domain])
    #         model_values = self._get_models(domain)
    #
    #         if filter_domain:
    #             # fetch new counters
    #             domain = expression.AND([search_domain, category_domain, filter_domain])
    #             model_count = {
    #                 model['id']: model['__count']
    #                 for model in self._get_models(domain)
    #             }
    #             # update result with new counters
    #             for model in model_values:
    #                 model['__count'] = model_count.get(model['id'], 0)
    #             print(
    #                 "model_valuesmodel_valuesmodel_valuesmodel_valuesmodel_valuesmodel_valuesmodel_valuesmodel_valuesmodel_values",
    #                 model_values)
    #         return {'values': model_values}
    #
    #     return super(Document, self).search_panel_select_multi_range(field_name, **kwargs)

class DTwelveDepartment(models.Model):
    _name = 'd.twelve.department'
    _description = 'D12 Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    parent_department_id = fields.Many2one('d.twelve.department', "Parent Department", index=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True,
                                      help='Get you bank statements in electronic format from your bank and'
                                           ' select them here.')
    first_char = fields.Char(string="First Char", compute='firstchar')
    display = fields.Char(string="First Char", compute='firstchar')

    @api.depends('name')
    def firstchar(self):
        for f in self:
            if f.name:
                f.first_char = f.name.split('.')[:1][0].strip()[:2]
                f.display = f.name.split('.', 1)[1].strip()[:70]






