# Setup Scripts

Scripts for installing and configuring the Extended Attendance module.

## Scripts

### Core Setup
- `update_module_list.py` - Install Extended Attendance module
- `upgrade_module.py` - Upgrade existing installation

### Extended Setup  
- `install_extended_attendance.py` - Comprehensive installation
- `setup_extended_attendance.py` - Advanced setup options
- `setup_demo.py` - Demo data setup

### Legacy
- ~~`install_fastapi_modules.py`~~ - Removed (FastAPI no longer used)

## Usage

1. **Basic Installation**:
   ```bash
   python3 scripts/setup/update_module_list.py
   ```

2. **Upgrade Existing**:
   ```bash
   python3 scripts/setup/upgrade_module.py
   ```

3. **Demo Data**:
   ```bash
   python3 scripts/setup/setup_demo.py
   ```
