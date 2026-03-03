from odoo import http
from odoo.http import request


class HoboxPublic(http.Controller):

    # ── LANDING PAGE ─────────────────────────────────────────────────────────
    @http.route('/hobox/landing', auth='public', website=True)
    def landing(self, **kw):
        return request.render('hobox_fulfillment.hobox_landing')

    # ── REGISTRATION FORM ─────────────────────────────────────────────────────
    @http.route('/hobox/register', auth='public', website=True)
    def register(self, **kw):
        return request.render('hobox_fulfillment.hobox_register')

    @http.route('/hobox/register/submit', auth='public', website=True, methods=['POST'], csrf=True)
    def register_submit(self, **post):
        """Validate and create a hobox.registration record, then redirect to success."""
        required_fields = ['first_name', 'last_name', 'phone', 'email',
                           'company_name', 'store_url', 'platform_type']
        errors = {}
        for f in required_fields:
            if not post.get(f, '').strip():
                errors[f] = 'This field is required.'

        # Duplicate email check
        if not errors.get('email'):
            existing = request.env['hobox.registration'].sudo().search(
                [('email', '=', post['email'].strip()),
                 ('state', 'in', ['pending', 'approved'])],
                limit=1,
            )
            if existing:
                errors['email'] = 'A registration request with this email already exists.'

        if errors:
            return request.render('hobox_fulfillment.hobox_register', {
                'errors': errors,
                'values': post,
            })

        platform_valid = [
            'shopify', 'woocommerce', 'salla', 'zid', 'tiktok_shop',
            'noon', 'amazon', 'magento', 'excel_manual', 'other',
        ]
        platform = post.get('platform_type') if post.get('platform_type') in platform_valid else 'other'

        request.env['hobox.registration'].sudo().create({
            'first_name':    post['first_name'].strip(),
            'last_name':     post['last_name'].strip(),
            'phone':         post['phone'].strip(),
            'email':         post['email'].strip(),
            'company_name':  post['company_name'].strip(),
            'store_url':     post['store_url'].strip(),
            'platform_type': platform,
        })

        return request.redirect('/hobox/register/success')

    # ── SUCCESS PAGE ─────────────────────────────────────────────────────────
    @http.route('/hobox/register/success', auth='public', website=True)
    def register_success(self, **kw):
        return request.render('hobox_fulfillment.hobox_register_success')