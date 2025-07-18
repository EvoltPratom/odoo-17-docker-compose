#!/usr/bin/env python3
"""
Simple Swagger UI generator for existing Odoo HTTP controllers
Reads your existing controllers and generates OpenAPI/Swagger documentation
"""

import json
import re
from pathlib import Path

def extract_routes_from_controller(file_path):
    """Extract HTTP routes from Odoo controller file"""
    routes = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all @http.route decorators and their methods
    route_pattern = r'@http\.route\([\'"]([^\'"]+)[\'"].*?type=[\'"]([^\'"]+)[\'"].*?methods=\[([^\]]+)\].*?\)\s*def\s+(\w+)\(([^)]*)\):\s*"""([^"]*?)"""'
    
    matches = re.finditer(route_pattern, content, re.DOTALL)
    
    for match in matches:
        path = match.group(1)
        route_type = match.group(2)
        methods = match.group(3).replace("'", "").replace('"', "").split(', ')
        function_name = match.group(4)
        parameters = match.group(5)
        docstring = match.group(6).strip()
        
        # Parse parameters
        params = []
        if parameters:
            param_list = [p.strip() for p in parameters.split(',') if p.strip() and p.strip() != 'self']
            for param in param_list:
                if '=' in param:
                    name, default = param.split('=', 1)
                    params.append({
                        'name': name.strip(),
                        'required': False,
                        'default': default.strip()
                    })
                else:
                    params.append({
                        'name': param.strip(),
                        'required': True
                    })
        
        routes.append({
            'path': path,
            'methods': methods,
            'function': function_name,
            'type': route_type,
            'description': docstring,
            'parameters': params
        })
    
    return routes

def generate_openapi_spec(routes, title="Odoo API", version="1.0.0"):
    """Generate OpenAPI 3.0 specification"""
    
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "description": "Auto-generated API documentation for Odoo HTTP controllers",
            "version": version
        },
        "servers": [
            {
                "url": "http://localhost:10017",
                "description": "Local Odoo server"
            }
        ],
        "paths": {}
    }
    
    for route in routes:
        path = route['path']
        if path not in spec['paths']:
            spec['paths'][path] = {}
        
        for method in route['methods']:
            method_lower = method.lower()
            
            operation = {
                "summary": route['function'].replace('_', ' ').title(),
                "description": route['description'] or f"Endpoint: {route['function']}",
                "operationId": f"{method_lower}_{route['function']}",
                "tags": ["Attendance API"]
            }
            
            # Add parameters
            if route['parameters']:
                operation['parameters'] = []
                for param in route['parameters']:
                    operation['parameters'].append({
                        "name": param['name'],
                        "in": "query" if route['type'] == 'http' else "body",
                        "required": param['required'],
                        "schema": {"type": "string"},
                        "description": f"Parameter: {param['name']}"
                    })
            
            # Add request body for JSON endpoints
            if route['type'] == 'json' and method_lower in ['post', 'put', 'patch']:
                operation['requestBody'] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    param['name']: {"type": "string", "description": f"Parameter: {param['name']}"}
                                    for param in route['parameters']
                                }
                            }
                        }
                    }
                }
            
            # Add responses
            operation['responses'] = {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "message": {"type": "string"},
                                    "data": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Bad request"
                },
                "500": {
                    "description": "Internal server error"
                }
            }
            
            spec['paths'][path][method_lower] = operation
    
    return spec

def generate_swagger_html(openapi_spec):
    """Generate HTML page with Swagger UI"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Odoo API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                spec: {json.dumps(openapi_spec, indent=2)},
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>
"""
    return html

def main():
    """Generate Swagger documentation for Odoo controllers"""
    
    # Extract routes from your controller
    controller_file = "addons/extended_attendance/controllers/attendance_api.py"
    
    if not Path(controller_file).exists():
        print(f"❌ Controller file not found: {controller_file}")
        return
    
    print("🔍 Extracting routes from controller...")
    routes = extract_routes_from_controller(controller_file)
    
    print(f"✅ Found {len(routes)} routes:")
    for route in routes:
        print(f"  - {route['methods']} {route['path']} -> {route['function']}")
    
    # Generate OpenAPI spec
    print("📝 Generating OpenAPI specification...")
    openapi_spec = generate_openapi_spec(routes, "Extended Attendance API", "1.0.0")
    
    # Generate Swagger HTML
    print("🎨 Generating Swagger UI...")
    swagger_html = generate_swagger_html(openapi_spec)
    
    # Save files
    with open("swagger.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)
    
    with open("swagger.html", "w") as f:
        f.write(swagger_html)
    
    print("🎉 Swagger documentation generated!")
    print("📄 OpenAPI spec: swagger.json")
    print("🌐 Swagger UI: swagger.html")
    print("🚀 Open swagger.html in your browser to view the API docs")

if __name__ == "__main__":
    main()
