from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class HoboxPortal(http.Controller):

    def _get_partner(self):
        partner = request.env.user.partner_id
        if not partner.is_hobox_client:
            return None
        return partner

    # ── HOME → redirect to dashboard ────────────────────────────────────
    @http.route('/hobox', auth='user', website=True)
    def index(self, **kw):
        return request.redirect('/hobox/dashboard')

    # ── DASHBOARD ────────────────────────────────────────────────────────
    @http.route('/hobox/dashboard', auth='user', website=True)
    def dashboard(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')

        orders    = request.env['sale.order'].sudo().search(
            [('hobox_client_id', '=', partner.id)])
        receipts  = request.env['stock.picking'].sudo().search([
            ('hobox_client_id', '=', partner.id),
            ('picking_type_code', '=', 'incoming')])
        deliveries = request.env['stock.picking'].sudo().search([
            ('hobox_client_id', '=', partner.id),
            ('picking_type_code', '=', 'outgoing')])
        products  = request.env['product.template'].sudo().search(
            [('hobox_client_id', '=', partner.id)])
        cod       = request.env['hobox.cod.settlement'].sudo().search(
            [('partner_id', '=', partner.id)])
        withdrawals = request.env['hobox.withdrawal.request'].sudo().search(
            [('partner_id', '=', partner.id)])

        # ── KPI aggregates ───────────────────────────────────────────────
        total_orders       = len(orders)
        completed_orders   = len(orders.filtered(lambda o: o.hobox_state == 'completed'))
        inprogress_orders  = len(orders.filtered(
            lambda o: o.hobox_state in ['received', 'processing', 'ready']))
        cod_orders         = len(orders.filtered(lambda o: o.is_cod))

        total_products     = len(products)
        low_stock          = len(products.filtered(
            lambda p: p.qty_available <= p.low_stock_threshold))

        total_receipts     = len(receipts)
        pending_receipts   = len(receipts.filtered(lambda r: r.state != 'done'))

        delivered          = len(deliveries.filtered(
            lambda d: d.carrier_tracking_state == 'delivered'))
        failed_deliveries  = len(deliveries.filtered(
            lambda d: d.carrier_tracking_state == 'failed'))

        net_cod_total      = sum(cod.mapped('net_client_amount'))
        pending_withdrawals = len(withdrawals.filtered(
            lambda w: w.state in ['draft', 'requested', 'approved']))

        # ── Recent activity (last 5 of each) ─────────────────────────────
        recent_orders     = orders.sorted('date_order',  reverse=True)[:5]
        recent_deliveries = deliveries.sorted('date_done', reverse=True)[:5]

        return request.render('hobox_fulfillment.hobox_dashboard', {
            'partner':            partner,
            # order stats
            'total_orders':       total_orders,
            'completed_orders':   completed_orders,
            'inprogress_orders':  inprogress_orders,
            'cod_orders':         cod_orders,
            # inventory stats
            'total_products':     total_products,
            'low_stock':          low_stock,
            # receipt stats
            'total_receipts':     total_receipts,
            'pending_receipts':   pending_receipts,
            # delivery stats
            'delivered':          delivered,
            'failed_deliveries':  failed_deliveries,
            # finance stats
            'net_cod_total':      net_cod_total,
            'pending_withdrawals': pending_withdrawals,
            # recent lists
            'recent_orders':      recent_orders,
            'recent_deliveries':  recent_deliveries,
        })

    # ── PROFILE ─────────────────────────────────────────────────────────
    @http.route('/hobox/profile', auth='user', website=True)
    def profile(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        return request.render('hobox_fulfillment.hobox_profile', {'partner': partner})

    @http.route('/hobox/profile/edit', auth='user', website=True)
    def profile_edit(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        return request.render('hobox_fulfillment.hobox_profile_edit', {'partner': partner})

    @http.route('/hobox/profile/save', auth='user', website=True, methods=['POST'])
    def profile_save(self, **post):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        partner.sudo().write({
            'name':                 post.get('name'),
            'email':                post.get('email'),
            'phone':                post.get('phone'),
            'default_storage_type': post.get('default_storage_type'),
        })
        return request.redirect('/hobox/profile')

    # ── ORDERS ──────────────────────────────────────────────────────────
    @http.route('/hobox/orders', auth='user', website=True)
    def orders(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        orders = request.env['sale.order'].sudo().search(
            [('hobox_client_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_orders', {'orders': orders})

    # ── PRODUCTS ────────────────────────────────────────────────────────
    @http.route('/hobox/products', auth='user', website=True)
    def products(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        products = request.env['product.template'].sudo().search(
            [('hobox_client_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_products', {'products': products})

    # ── RECEIPTS ────────────────────────────────────────────────────────
    @http.route('/hobox/receipts', auth='user', website=True)
    def receipts(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        receipts = request.env['stock.picking'].sudo().search([
            ('hobox_client_id', '=', partner.id),
            ('picking_type_code', '=', 'incoming'),
        ])
        return request.render('hobox_fulfillment.hobox_receipts', {'receipts': receipts})

    # ── DELIVERIES ──────────────────────────────────────────────────────
    @http.route('/hobox/deliveries', auth='user', website=True)
    def deliveries(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        deliveries = request.env['stock.picking'].sudo().search([
            ('hobox_client_id', '=', partner.id),
            ('picking_type_code', '=', 'outgoing'),
        ])
        return request.render('hobox_fulfillment.hobox_deliveries', {'deliveries': deliveries})

    # ── COD SETTLEMENTS ─────────────────────────────────────────────────
    @http.route('/hobox/cod', auth='user', website=True)
    def cod(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        cod_settlements = request.env['hobox.cod.settlement'].sudo().search(
            [('partner_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_cod', {'cod_settlements': cod_settlements})

    # ── WITHDRAWALS ─────────────────────────────────────────────────────
    @http.route('/hobox/withdrawals', auth='user', website=True)
    def withdrawals(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        withdrawals = request.env['hobox.withdrawal.request'].sudo().search(
            [('partner_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_withdrawals',
                              {'withdrawals': withdrawals})

    @http.route('/hobox/withdrawals/new', auth='user', website=True)
    def withdrawal_new(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        bank_accounts = request.env['res.partner.bank'].sudo().search(
            [('partner_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_withdrawal_new',
                              {'bank_accounts': bank_accounts})

    @http.route('/hobox/withdrawals/save', auth='user', website=True, methods=['POST'])
    def withdrawal_save(self, **post):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        request.env['hobox.withdrawal.request'].sudo().create({
            'partner_id':      partner.id,
            'amount_requested': float(post.get('amount_requested', 0)),
            'bank_account_id': int(post.get('partner_bank_id')) if post.get('partner_bank_id') else False,
            'notes':           post.get('note'),
        })
        return request.redirect('/hobox/withdrawals')

    # ── INTEGRATIONS ────────────────────────────────────────────────────
    @http.route('/hobox/integrations', auth='user', website=True)
    def integrations(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        integrations = request.env['hobox.platform.integration'].sudo().search(
            [('partner_id', '=', partner.id)])
        return request.render('hobox_fulfillment.hobox_integrations',
                              {'integrations': integrations})

    @http.route('/hobox/integrations/new', auth='user', website=True)
    def integration_new(self, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        return request.render('hobox_fulfillment.hobox_integration_form',
                              {'integration': None})

    @http.route('/hobox/integrations/<int:integration_id>/edit', auth='user', website=True)
    def integration_edit(self, integration_id, **kw):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        integration = request.env['hobox.platform.integration'].sudo().browse(integration_id)
        if integration.partner_id.id != partner.id:
            return request.redirect('/hobox/integrations')
        return request.render('hobox_fulfillment.hobox_integration_form',
                              {'integration': integration})

    @http.route('/hobox/integrations/<integration_id>/save', auth='user', website=True,
                methods=['POST'])
    def integration_save(self, integration_id, **post):
        partner = self._get_partner()
        if not partner:
            return request.redirect('/')
        vals = {
            'name':          post.get('name'),
            'platform_type': post.get('platform_type'),
            'api_url':       post.get('api_url'),
            'api_key':       post.get('api_key'),
            'api_secret':    post.get('api_secret'),
            'auto_import':   bool(post.get('auto_import')),
            'test_mode':     bool(post.get('test_mode')),
            'notes':         post.get('note'),
        }
        if integration_id == 'new':
            vals['partner_id'] = partner.id
            request.env['hobox.platform.integration'].sudo().create(vals)
        else:
            integration = request.env['hobox.platform.integration'].sudo().browse(
                int(integration_id))
            if integration.partner_id.id == partner.id:
                integration.write(vals)
        return request.redirect('/hobox/integrations')