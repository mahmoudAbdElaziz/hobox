from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_hobox_client = fields.Boolean(string='HOBOX Client')
    hobox_client_code = fields.Char(string='Client Code', copy=False, readonly=True)
    hobox_state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ], string='Status', default='draft')

    date = fields.Date(string='Agreement Date')
    contract_document = fields.Binary(string='Contract Document')
    contract_filename = fields.Char()

    warehouse_id = fields.Many2one('stock.warehouse', string='Dedicated Warehouse')
    default_storage_type = fields.Selection([
        ('unit', 'Unit'),
        ('shelf', 'Shelf'),
        ('pallet', 'Pallet'),
    ], string='Default Storage Type', default='unit')

    hobox_payment_terms_id = fields.Many2one('account.payment.term', string='Payment Terms')
    hobox_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    integration_ids = fields.One2many(
        'hobox.platform.integration', 'partner_id', string='Integrations')
    integration_count = fields.Integer(compute='_compute_integration_count')

    hobox_notes = fields.Text(string='Internal Notes')

    integration_count = fields.Integer(compute='_compute_integration_count')

    hobox_order_count = fields.Integer(compute='_compute_hobox_counts')
    hobox_product_count = fields.Integer(compute='_compute_hobox_counts')
    hobox_receipt_count = fields.Integer(compute='_compute_hobox_counts')
    hobox_delivery_count = fields.Integer(compute='_compute_hobox_counts')
    hobox_cod_count = fields.Integer(compute='_compute_hobox_counts')
    hobox_withdrawal_count = fields.Integer(compute='_compute_hobox_counts')

    @api.depends('integration_ids')
    def _compute_integration_count(self):
        for rec in self:
            rec.integration_count = len(rec.integration_ids)

    @api.depends()
    def _compute_hobox_counts(self):
        for rec in self:
            rec.hobox_order_count = self.env['sale.order'].search_count(
                [('hobox_client_id', '=', rec.id)])
            rec.hobox_product_count = self.env['product.template'].search_count(
                [('hobox_client_id', '=', rec.id)])
            rec.hobox_receipt_count = self.env['stock.picking'].search_count(
                [('hobox_client_id', '=', rec.id), ('picking_type_code', '=', 'incoming')])
            rec.hobox_delivery_count = self.env['stock.picking'].search_count(
                [('hobox_client_id', '=', rec.id), ('picking_type_code', '=', 'outgoing')])
            rec.hobox_cod_count = self.env['hobox.cod.settlement'].search_count(
                [('partner_id', '=', rec.id)])
            rec.hobox_withdrawal_count = self.env['hobox.withdrawal.request'].search_count(
                [('partner_id', '=', rec.id)])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_hobox_client') and not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('hobox.client')
        return super().create(vals_list)

    def action_hobox_client_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('hobox_client_id', '=', self.id)],
            'context': {'default_hobox_client_id': self.id},
        }

    def action_hobox_client_products(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('hobox_client_id', '=', self.id)],
            'context': {'default_hobox_client_id': self.id},
        }

    def action_hobox_client_receipts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receipts',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('hobox_client_id', '=', self.id), ('picking_type_code', '=', 'incoming')],
            'context': {'default_hobox_client_id': self.id},
        }

    def action_hobox_client_deliveries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deliveries',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('hobox_client_id', '=', self.id), ('picking_type_code', '=', 'outgoing')],
            'context': {'default_hobox_client_id': self.id},
        }

    def action_hobox_client_cod(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'COD Settlements',
            'res_model': 'hobox.cod.settlement',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_hobox_client_integrations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Platform Integrations',
            'res_model': 'hobox.platform.integration',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_hobox_client_withdrawals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Withdrawal Requests',
            'res_model': 'hobox.withdrawal.request',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }