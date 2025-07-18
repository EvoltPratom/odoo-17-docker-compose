# Quick Setup Guide for Attendance System

## 1. Create Database (Manual)

1. **Open Odoo Web Interface**: Go to http://localhost:10017
2. **Create Database**:
   - Database Name: `attendance_demo`
   - Email: `admin@demo.com`
   - Password: `admin`
   - Language: `English`
   - Demo Data: ✅ Check this box
   - Click "Create Database"

## 2. Install HR Attendance Module

1. **Go to Apps**: Click on "Apps" in the main menu
2. **Search for "Attendance"**: Type "attendance" in the search box
3. **Install**: Click "Install" on the "Attendance" module
4. **Wait**: Let it install (may take a few minutes)

## 3. Create Test Employees

1. **Go to Employees**: Click on "Employees" in the main menu
2. **Create New Employee**:
   - Name: `John Doe`
   - Email: `john@demo.com`
   - Employee ID: `EMP001`
   - Save

3. **Create More Employees**:
   - Name: `Jane Smith`, Email: `jane@demo.com`, ID: `EMP002`
   - Name: `Bob Johnson`, Email: `bob@demo.com`, ID: `EMP003`

## 4. Update Frontend Configuration

Update the database name in the custom frontend:

1. Open http://localhost:8080
2. Click the settings icon (⚙️) in the top right
3. Update settings:
   - Database Name: `attendance_demo`
   - Username: `admin`
   - Password: `admin`
4. Click "Save"
5. Refresh the page

## 5. Test the System

1. **Select an Employee**: Choose from the dropdown
2. **Clock In**: Click the "Clock In" button
3. **Clock Out**: Click the "Clock Out" button
4. **View Records**: Check the "Recent Attendance" section
5. **Export Data**: Use the export functionality

## URLs

- **Odoo Admin**: http://localhost:10017
- **Custom Frontend**: http://localhost:8080

## Credentials

- **Username**: admin
- **Password**: admin
- **Database**: attendance_demo

---

That's it! Your attendance system should now be working with both the custom frontend and Odoo backend.
