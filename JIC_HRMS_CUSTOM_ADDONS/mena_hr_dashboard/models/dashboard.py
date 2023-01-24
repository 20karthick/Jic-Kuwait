from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.http import request

class HrDashboard(models.Model):
   _name = 'hr.dashboard'


   @api.model
   def get_tiles_data(self):
       return {
           'total_projects': 5,
           'total_tasks': 66,
           'total_employees': 7,
       }

   @api.model
   def get_employee_menu(self):
       ir_model_data = self.env['ir.model.data']
       menu_id = ir_model_data._xmlid_lookup("hr.menu_hr_root")[2]
       # action_id = ir_model_data._xmlid_lookup('hr.open_view_employee_list_my')[2]
       url = "/web#menu_id=%s&model=hr.employee&view_type=kanban" % (menu_id)
       return {'redirect': url}

   @api.model
   def get_recruitment_menu(self):
       ir_model_data = self.env['ir.model.data']
       menu_id = ir_model_data._xmlid_lookup("hr_recruitment.menu_hr_recruitment_root")[2]
       url = "/web#menu_id=%s&model=hr.job&view_type=kanban" % (menu_id)
       return {'redirect': url}

   @api.model
   def get_payroll_menu(self):
       ir_model_data = self.env['ir.model.data'].sudo()
       menu_id = ir_model_data._xmlid_lookup("hr_payroll_community.menu_hr_payroll_community_root")[2]
       url = "/web#menu_id=%s&model=hr.payslip&view_type=list" % (menu_id)
       return {'redirect': url}


class InheritMenu(models.Model):
    _inherit = 'ir.ui.menu'


    description = fields.Char('Description',size=173)
    image = fields.Binary(string="Image")

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus).

        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data', 'description', 'image']
        menu_roots = self.get_user_roots()
        menu_roots_data = menu_roots.read(fields) if menu_roots else []
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': [menu['id'] for menu in menu_roots_data],
        }

        all_menus = {'root': menu_root}

        if not menu_roots_data:
            return all_menus

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menus_domain = [('id', 'child_of', menu_roots.ids)]
        blacklisted_menu_ids = self._load_menus_blacklist()
        if blacklisted_menu_ids:
            menus_domain = expression.AND([menus_domain, [('id', 'not in', blacklisted_menu_ids)]])
        menus = self.search(menus_domain)
        menu_items = menus.read(fields)
        xmlids = (menu_roots + menus)._get_menuitems_xmlids()

        # add roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots_data)

        # set children ids and xmlids
        menu_items_map = {menu_item["id"]: menu_item for menu_item in menu_items}
        for menu_item in menu_items:
            menu_item.setdefault('children', [])
            parent = menu_item['parent_id'] and menu_item['parent_id'][0]
            menu_item['xmlid'] = xmlids.get(menu_item['id'], "")
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item['id'])
        all_menus.update(menu_items_map)

        # sort by sequence
        for menu_id in all_menus:
            all_menus[menu_id]['children'].sort(key=lambda id: all_menus[id]['sequence'])

        # recursively set app ids to related children
        def _set_app_id(app_id, menu):
            menu['app_id'] = app_id
            for child_id in menu['children']:
                _set_app_id(app_id, all_menus[child_id])

        for app in menu_roots_data:
            app_id = app['id']
            _set_app_id(app_id, all_menus[app_id])

        # filter out menus not related to an app (+ keep root menu)
        all_menus = {menu['id']: menu for menu in all_menus.values() if menu.get('app_id')}
        all_menus['root'] = menu_root

        return all_menus

    def load_web_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus) and
        processes them to be used by the webclient. Mainly, it associates with
        each application (top level menu) the action of its first child menu
        that is associated with an action (recursively), i.e. with the action
        to execute when the opening the app.

        :return: the menus (including the images in Base64)
        """
        menus = self.load_menus(debug)

        web_menus = {}
        for menu in menus.values():
            if not menu['id']:
                # special root menu case
                web_menus['root'] = {
                    "id": 'root',
                    "name": menu['name'],
                    "children": menu['children'],
                    "appID": False,
                    "xmlid": "",
                    "actionID": False,
                    "actionModel": False,
                    "webIcon": None,
                    "webIconData": None,
                    "backgroundImage": menu.get('backgroundImage'),
                }
            else:
                action = menu['action']

                if menu['id'] == menu['app_id']:
                    # if it's an app take action of first (sub)child having one defined
                    child = menu
                    while child and not action:
                        action = child['action']
                        child = menus[child['children'][0]] if child['children'] else False

                action_model, action_id = action.split(',') if action else (False, False)
                action_id = int(action_id) if action_id else False
                web_menus[menu['id']] = {
                    "id": menu['id'],
                    "name": menu['name'],
                    "children": menu['children'],
                    "appID": menu['app_id'],
                    "xmlid": menu['xmlid'],
                    "actionID": action_id,
                    "actionModel": action_model,
                    "webIcon": menu['web_icon'],
                    "webIconData": menu['web_icon_data'],
                    "des": menu['description'],
                    "image": menu['image'],
                }

        return web_menus


