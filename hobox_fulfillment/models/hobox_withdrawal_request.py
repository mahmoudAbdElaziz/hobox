from odoo import models, fields, api


class HoboxWithdrawalRequest(models.Model):
    _name = 'hobox.withdrawal.request'
    _description = 'HOBOX Withdrawal Request'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', copy=False, readonly=True, default='New')
    partner_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='Client', required=True, tracking=True)
    request_date = fields.Date(string='Request Date', required=True,
        default=fields.Date.today)
    amount_requested = fields.Float(string='Amount Requested', required=True, tracking=True)
    amount_approved = fields.Float(string='Amount Approved', tracking=True)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account',
        domain="[('partner_id', '=', partner_id)]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    vendor_bill_id = fields.Many2one('account.move', string='Vendor Bill', readonly=True)
    transfer_ref = fields.Char(string='Transfer Reference')
    processed_date = fields.Date(string='Processed Date')
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hobox.withdrawal')
        return super().create(vals_list)

    def action_request(self):
        self.write({'state': 'requested'})

    def action_approve(self):
        self.write({'state': 'approved', 'approved_by': self.env.user.id})

    def action_process(self):
        self.write({'state': 'processed', 'processed_date': fields.Date.today()})

    def action_reject(self):
        self.write({'state': 'rejected'})