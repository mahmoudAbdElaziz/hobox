from odoo import models, fields, api


class HoboxRegistration(models.Model):
    _name = 'hobox.registration'
    _description = 'HOBOX Client Registration Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company_name'
    _order = 'create_date desc'

    name = fields.Char(string='Reference', readonly=True, copy=False, default='New')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email', required=True)
    company_name = fields.Char(string='Company Name', required=True)
    store_url = fields.Char(string='Store URL', required=True)
    platform_type = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('salla', 'Salla'),
        ('zid', 'Zid'),
        ('tiktok_shop', 'TikTok Shop'),
        ('noon', 'Noon'),
        ('amazon', 'Amazon'),
        ('magento', 'Magento'),
        ('excel_manual', 'Manual (Excel)'),
        ('other', 'Other'),
    ], string='Platform', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Created Partner', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hobox.registration')
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            partner = self.env['res.partner'].create({
                'name': '%s %s' % (rec.first_name, rec.last_name),
                'email': rec.email,
                'phone': rec.phone,
                'company_name': rec.company_name,
                'website': rec.store_url,
                'is_hobox_client': True,
                'ref': self.env['ir.sequence'].next_by_code('hobox.client'),
            })
            rec.write({'state': 'approved', 'partner_id': partner.id})

    def action_reject(self):
        self.write({'state': 'rejected'})