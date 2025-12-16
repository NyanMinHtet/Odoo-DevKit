# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SwaggerUi(http.Controller):

    @http.route('/swagger/ui', type='http', auth='user', website=True)
    def swagger_ui(self, **kw):
        return request.render('web_swagger_ui.swagger_ui_template', {})
