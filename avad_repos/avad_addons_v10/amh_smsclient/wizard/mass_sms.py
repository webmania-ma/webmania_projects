##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import re

class part_sms(models.TransientModel):
    _name = 'part.sms'

    def _default_get_gateway(self,fields=None):
        context =self._context
        if context is None:
            context = {}
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False


    def _merge_message(self, message, object, partner, context=None):
        def merge(match):
            exp = str(match.group()[2: -2]).strip()
            result = eval(exp, {'object': object, 'partner': partner})
            if result in (None, False):
                return str("--------")
            return str(result)
        com = re.compile('(\[\[.+?\]\])')
        msg = com.sub(merge, message)
        return msg

    def sms_mass_send(self):
        context = self._context or {}
        datas = {}
        gateway_id = self[0].gateway.id
        client_obj = self.env['sms.smsclient']
        partner_obj = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        for data in self :
            if not data.gateway:
                raise ValidationError(_('No Gateway Found'))
            else:
                for partner in partner_obj.browse(active_ids):
                    data.mobile_to = partner.mobile or partner.parent_id.mobile
                    client_obj.with_context(context)._send_message(data)
        return True

    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True, defqult=_default_get_gateway)
    model_sms =  fields.Many2one('maritime.sms', 'Model SMS')
    body = fields.Text('Text', required=True)
    validity = fields.Integer('Validity',
                              help="The maximum time -in minute(s)- "
                                   "before the message is dropped")
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit'),
    ], 'Class',
        help="The sms class: flash(0),phone display(1),"
             "SIM(2),toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- to wait "
                                   "before sending the message")
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority',
        help="The priority of the message")
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding',
        help="The sms coding: 1 for 7 bit "
             "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help="An optional tag")
    nostop = fields.Selection([
        ('0', '0'),
        ('1', '1')
    ], 'NoStop',
        help='Do not display STOP clause in the message, this requires that this is not an advertising message')

    @api.onchange("gateway")
    def onchange_gateway_mass(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.gateway:
                return {}
            gateway = o.gateway
            return {
                'value': {
                    'validity': gateway.validity,
                    'classes': gateway.classes,
                    'deferred': gateway.deferred,
                    'priority': gateway.priority,
                    'coding': gateway.coding,
                    'tag': gateway.tag,
                    'nostop': gateway.nostop,
                }
            }

    @api.onchange("model_sms")
    def onchange_gateway_sms(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.model_sms:
                return {}
            gateway = o.model_sms
            return {
                'value': {
                    'body': gateway.description,

                }
            }


class part_sms_lead(models.TransientModel):
    _name = 'part.sms.lead'

    def _default_get_gateway(self,fields=None):
        context =self._context
        if context is None:
            context = {}
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False


    def _merge_message(self,message, object, partner, context=None):
        def merge(match):
            exp = str(match.group()[2: -2]).strip()
            result = eval(exp, {'object': object, 'partner': partner})
            if result in (None, False):
                return str("--------")
            return str(result)
        com = re.compile('(\[\[.+?\]\])')
        msg = com.sub(merge, message)
        return msg

    def sms_mass_send(self):
        context = self._context or {}
        datas = {}
        gateway_id = self[0].gateway.id
        client_obj = self.env['sms.smsclient']
        partner_obj = self.env['res.partner']
        active_ids = self._context.get('active_ids',[])
        if self._context.get('active_part_ids', False):
            active_ids = self._context.get('active_part_ids',[])

        for data in self :
            if not data.gateway:
                raise ValidationError(_('No Gateway Found'))
            else:
                for partner in partner_obj.browse(active_ids):
                    data.mobile_to = partner.mobile or partner.parent_id.mobile
                    client_obj.with_context(context)._send_message(data)
        return True


    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True, defqult=_default_get_gateway)
    model_sms = fields.Many2one('maritime.sms', 'Model SMS')
    body = fields.Text('Text', required=True)
    validity = fields.Integer('Validity',
                              help="The maximum time -in minute(s)- "
                                   "before the message is dropped")
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit'),
    ], 'Class',
        help="The sms class: flash(0),phone display(1),"
             "SIM(2),toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- to wait "
                                   "before sending the message")
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority',
        help="The priority of the message")
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding',
        help="The sms coding: 1 for 7 bit "
             "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help="An optional tag")
    nostop = fields.Selection([
        ('0', '0'),
        ('1', '1')
    ], 'NoStop',
        help='Do not display STOP clause in the message, this requires that this is not an advertising message')

    @api.onchange("model_sms")
    def onchange_gateway_sms(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.model_sms:
                return {}
            gateway = o.model_sms
            return {
                'value': {
                    'body': gateway.description,

                }
            }

    @api.onchange("gateway")
    def onchange_gateway_mass(self):
        context = self._context
        if context is None:
            context = {}
        for o in self:
            if not o.geteway:
                return {}
            gateway = o.gateway
            return {
                'value': {
                    'validity': gateway.validity,
                    'classes': gateway.classes,
                    'deferred': gateway.deferred,
                    'priority': gateway.priority,
                    'coding': gateway.coding,
                    'tag': gateway.tag,
                    'nostop': gateway.nostop,
                }
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
