# -*- coding: utf-8 -*-
import json
import re
from odoo import http
from odoo.http import request, Response, _generate_routing_rules


class SwaggerUi(http.Controller):
    """Serve Swagger UI and a generated OpenAPI spec for Odoo HTTP controllers."""

    DEFAULT_API_PREFIXES = ('/fs/api',)
    CONFIG_PARAMETER = 'web_swagger_ui.api_prefixes'
    PATH_PARAMETER_RE = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')

    @http.route('/swagger/ui', type='http', auth='user', website=True)
    def swagger_ui(self, **kw):
        return request.render('web_swagger_ui.swagger_ui_template', {})

    @http.route('/swagger/openapi.json', type='http', auth='user', website=True, csrf=False)
    def openapi_spec(self, **kw):
        env = request.env
        installed_modules = env['ir.module.module'].sudo().search([('state', '=', 'installed')]).mapped('name')
        rules = _generate_routing_rules(installed_modules, nodb_only=False)
        prefixes = self._get_api_prefixes()
        paths = {}

        for url, endpoint in rules:
            if not any(url.startswith(prefix) for prefix in prefixes):
                continue

            openapi_path = self._convert_odoo_path_to_openapi(url)
            methods = endpoint.routing.get('methods') or ['GET']
            path_item = paths.setdefault(openapi_path, {})

            for method in methods:
                method_name = method.lower()
                if method_name == 'head':
                    continue
                path_item[method_name] = self._build_operation(endpoint, url, method_name)

        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'FS Connector API',
                'version': '1.0.0',
                'description': 'Auto-generated OpenAPI spec for fs_connector routes.',
            },
            'paths': paths,
            'components': {
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT',
                    }
                }
            },
            'security': [
                {'bearerAuth': []}
            ],
        }
        return Response(json.dumps(spec), status=200, mimetype='application/json')

    def _get_api_prefixes(self):
        value = request.env['ir.config_parameter'].sudo().get_param(
            self.CONFIG_PARAMETER,
            ','.join(self.DEFAULT_API_PREFIXES),
        )
        if not value:
            return list(self.DEFAULT_API_PREFIXES)
        prefixes = [prefix.strip() for prefix in str(value).split(',') if prefix.strip()]
        return prefixes or list(self.DEFAULT_API_PREFIXES)

    def _convert_odoo_path_to_openapi(self, url):
        return self.PATH_PARAMETER_RE.sub(r'{\1}', url)

    def _build_operation(self, endpoint, url, method_name):
        func = getattr(endpoint, 'func', endpoint)
        operation_id = getattr(func, '__name__', method_name)
        summary = (func.__doc__ or '').strip() or operation_id.replace('_', ' ').title()

        parameters = self._extract_path_parameters(url)
        request_body = None
        if method_name in {'post', 'put', 'patch', 'delete'}:
            request_body = self._build_request_body_schema(func, url)

        operation = {
            'operationId': operation_id,
            'summary': summary,
            'responses': {
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'}
                        }
                    }
                }
            },
        }

        if parameters:
            operation['parameters'] = parameters
        if request_body is not None:
            operation['requestBody'] = request_body

        return operation

    def _build_request_body_schema(self, func, url):
        explicit_schema = getattr(func, 'swagger_request_body', None)
        if isinstance(explicit_schema, dict):
            return {
                'content': {
                    'application/json': {
                        'schema': explicit_schema
                    }
                },
                'required': False,
            }

        return None

    def _extract_path_parameters(self, url):
        names = self.PATH_PARAMETER_RE.findall(url)
        return [
            {
                'name': name,
                'in': 'path',
                'required': True,
                'schema': {'type': 'string'},
            }
            for name in names
        ]
