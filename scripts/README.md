# Scripts Directory

This directory contains utility scripts for managing the Extended Attendance Odoo module.

## Directory Structure

```
scripts/
├── setup/          # Module installation and setup scripts
├── testing/        # Testing and validation scripts
├── utils/          # Utility scripts for development
├── examples/       # Example usage scripts
├── frontend/       # Frontend and API documentation
├── legacy/         # Legacy/deprecated scripts
├── docker/         # Docker-related utilities
└── README.md       # This file
```

## Setup Scripts (`setup/`)

### `update_module_list.py`
- **Purpose**: Install or update the Extended Attendance module
- **Usage**: `python3 scripts/setup/update_module_list.py`
- **Description**: Connects to Odoo, updates module list, and installs the extended_attendance module

### `upgrade_module.py`
- **Purpose**: Upgrade an existing Extended Attendance module installation
- **Usage**: `python3 scripts/setup/upgrade_module.py`
- **Description**: Upgrades the module to reload demo data and apply changes

## Testing Scripts (`testing/`)

### `test_simple_module.py`
- **Purpose**: Test the simplified Extended Attendance module installation
- **Usage**: `python3 scripts/testing/test_simple_module.py`
- **Description**: Validates that all models are working and demo data is loaded

### `test_module_installation.py`
- **Purpose**: Comprehensive module installation test
- **Usage**: `python3 scripts/testing/test_module_installation.py`
- **Description**: Tests module installation and basic functionality

## Utility Scripts (`utils/`)

### `odoo_api_explorer.py`
- **Purpose**: Interactive Odoo API explorer
- **Usage**: `python3 scripts/utils/odoo_api_explorer.py`
- **Description**: Provides an interactive interface to explore Odoo models and data

### `find_credentials.py`
- **Purpose**: Find and test Odoo database credentials
- **Usage**: `python3 scripts/utils/find_credentials.py`
- **Description**: Discovers available databases and tests authentication

### `check_odoo.py`
- **Purpose**: Health check for Odoo installation
- **Usage**: `python3 scripts/utils/check_odoo.py`
- **Description**: Verifies Odoo is running and accessible

### `check_models.py`
- **Purpose**: Validate Extended Attendance models
- **Usage**: `python3 scripts/utils/check_models.py`
- **Description**: Checks if all required models are properly installed

## Example Scripts (`examples/`)

### `extended_attendance_example.py`
- **Purpose**: Comprehensive usage example
- **Usage**: `python3 scripts/examples/extended_attendance_example.py`
- **Description**: Shows how to use the Extended Attendance API

### `simple_extended_attendance.py`
- **Purpose**: Simple usage example
- **Usage**: `python3 scripts/examples/simple_extended_attendance.py`
- **Description**: Basic example of attendance tracking

### `quick_start.py`
- **Purpose**: Quick start demonstration
- **Usage**: `python3 scripts/examples/quick_start.py`
- **Description**: Fast setup and demo of core features

## Frontend Scripts (`frontend/`)

### `real_frontend_server.py`
- **Purpose**: Frontend development server
- **Usage**: `python3 scripts/frontend/real_frontend_server.py`
- **Description**: Serves the custom frontend interface

### `swagger.html` / `swagger.json`
- **Purpose**: API documentation
- **Description**: Interactive API documentation and specifications

## Legacy Scripts (`legacy/`)

Contains deprecated scripts that are kept for reference:
- `attendance_manager.py` - Old attendance management
- `employee_manager.py` - Old employee management
- `export_manager.py` - Old export functionality
- `create_backend_data.py` - Old data creation scripts

## Configuration

All scripts use the following default connection parameters:
- **URL**: http://localhost:10017
- **Database**: extended_attendance
- **Username**: admin@demo.com
- **Password**: admin

## Prerequisites

- Docker Compose environment running
- Odoo 17 container accessible on port 10017
- Python 3 with xmlrpc.client module

## Quick Start

1. **Install the module**:
   ```bash
   python3 scripts/setup/update_module_list.py
   ```

2. **Test the installation**:
   ```bash
   python3 scripts/testing/test_simple_module.py
   ```

3. **Explore the API**:
   ```bash
   python3 scripts/utils/odoo_api_explorer.py
   ```

## Notes

- Scripts are designed to be run from the project root directory
- All scripts include error handling and detailed output
- Connection parameters can be modified within each script if needed
