# Scripts Directory

This directory contains utility scripts for managing the Extended Attendance Odoo module.

## Directory Structure

```
scripts/
├── setup/          # Module installation and setup scripts
├── testing/        # Testing and validation scripts
├── utils/          # Utility scripts for development
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
