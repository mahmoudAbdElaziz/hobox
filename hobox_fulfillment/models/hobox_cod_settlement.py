from odoo import models, fields, api


class HoboxCodSettlement(models.Model):
    _name = 'hobox.cod.settlement'
    _description = 'HOBOX COD Settlement'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', copy=False, readonly=True, default='New')
    partner_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='Client', required=True, tracking=True)
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier', required=True)
    settlement_date = fields.Date(string='Settlement Date', required=True)
    sale_order_ids = fields.Many2many('sale.order', string='COD Orders',
        domain=[('is_cod', '=', True)])

    total_cod_collected = fields.Float(string='Total COD Collected', tracking=True)
    shipping_fees = fields.Float(string='Shipping Fees')
    service_fees = fields.Float(string='Service Fees')
    other_deductions = fields.Float(string='Other Deductions')
    net_client_amount = fields.Float(string='Net Client Amount', compute='_compute_net', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('transferred', 'Transferred'),
    ], string='Status', default='draft', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    transfer_ref = fields.Char(string='Transfer Reference')
    notes = fields.Text(string='Notes')

    @api.depends('total_cod_collected', 'shipping_fees', 'service_fees', 'other_deductions')
    def _compute_net(self):
        for rec in self:
            rec.net_client_amount = (
                rec.total_cod_collected
                - rec.shipping_fees
                - rec.service_fees
                - rec.other_deductions
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hobox.cod.settlement')
        return super().create(vals_list)