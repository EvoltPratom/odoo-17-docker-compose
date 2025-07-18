# 🎯 Odoo Attendance Dashboard

A modern web frontend for managing Odoo attendance data with real-time API integration.

## ✨ Features

- **Real-time Odoo API Integration** - Direct connection to your Odoo instance
- **Employee Management** - View, create, and manage employees
- **Attendance Tracking** - Record check-ins/check-outs and view attendance history
- **Live Statistics** - Real-time dashboard with attendance metrics
- **Export Functionality** - Export attendance data using the custom export module
- **Responsive Design** - Works on desktop and mobile devices
- **Modern UI** - Clean, intuitive interface with smooth animations

## 🚀 Quick Start

### 1. Start the Frontend Server

```bash
cd new_frontend
python3 server.py
```

The server will start on **http://localhost:8080**

### 2. Open in Browser

Navigate to **http://localhost:8080** in your web browser.

### 3. Connect to Odoo

Use the login form with your Odoo credentials:
- **URL**: `http://localhost:10017`
- **Database**: `attendance_test`
- **Username**: `bishantad@gmail.com`
- **Password**: `12345`

## 📋 What You Can Do

### 👥 Employee Management
- **View all employees** with their details and current status
- **Search employees** by name, email, or barcode
- **Add new employees** with contact information
- **View employee details** including recent attendance history

### ⏰ Attendance Management
- **Record check-ins and check-outs** for employees
- **View recent attendance** with filtering options (today, week, month)
- **See real-time status** of who's present/absent
- **Track working hours** and attendance patterns

### 📊 Dashboard Analytics
- **Total employees** count
- **Present today** - employees currently at work
- **Total hours** worked today
- **Attendance records** count for today

### 📤 Data Export
- **Export attendance data** to JSON files
- **Configure export settings** (date ranges, employee filters)
- **Download reports** for analysis

## 🛠️ Technical Details

### Architecture
```
Browser (Frontend) ↔ Python Server (Proxy) ↔ Odoo (XML-RPC API)
```

### Components
- **HTML/CSS/JavaScript** - Modern responsive frontend
- **Python HTTP Server** - Proxy server to handle CORS and API calls
- **Odoo XML-RPC** - Direct integration with Odoo backend

### API Endpoints
- `POST /api/connect` - Authenticate with Odoo
- `POST /api/call` - Make Odoo API calls (search, read, create, write, etc.)

### Files Structure
```
new_frontend/
├── index.html          # Main HTML page
├── styles.css          # CSS styling
├── app.js             # Frontend JavaScript logic
├── odoo-api.js        # Odoo API client
├── server.py          # Python proxy server
└── README.md          # This file
```

## 🔧 Configuration

### Server Configuration
Edit `server.py` to change default settings:

```python
FRONTEND_PORT = 8080                    # Frontend server port
ODOO_URL = 'http://localhost:10017'     # Odoo server URL
ODOO_DB = 'attendance_test'             # Default database
ODOO_USERNAME = 'bishantad@gmail.com'   # Default username
ODOO_PASSWORD = '12345'                 # Default password
```

### Frontend Configuration
The frontend automatically uses the credentials you enter in the login form.

## 🎨 UI Features

### Modern Design
- **Gradient backgrounds** and smooth animations
- **Card-based layout** for organized information
- **Responsive grid system** that adapts to screen size
- **Icon integration** with Font Awesome icons

### Interactive Elements
- **Modal dialogs** for forms and detailed views
- **Toast notifications** for user feedback
- **Real-time updates** when data changes
- **Search and filtering** capabilities

### Status Indicators
- **Connection status** - Shows if connected to Odoo
- **Employee status** - Present/Absent/Left indicators
- **Attendance actions** - Check-in/Check-out badges
- **Loading states** - Spinners and progress indicators

## 🔍 Troubleshooting

### Connection Issues
1. **Make sure Odoo is running**: `docker-compose ps`
2. **Check the URL and port**: Default is `localhost:10017`
3. **Verify credentials**: Use the correct database name and password
4. **Check browser console**: Look for error messages

### Server Issues
1. **Port already in use**: Change `FRONTEND_PORT` in `server.py`
2. **Python dependencies**: Make sure you have Python 3.6+
3. **CORS errors**: The proxy server handles CORS automatically

### Data Issues
1. **No employees showing**: Create employees first using the "Add Employee" button
2. **No attendance records**: Record some attendance using the "Record Attendance" button
3. **Export not working**: Make sure the attendance_export module is installed

## 🚀 Next Steps

### Enhancements You Can Add
1. **Real-time updates** - WebSocket integration for live data
2. **Advanced filtering** - More sophisticated search and filter options
3. **Charts and graphs** - Visual analytics with Chart.js or D3.js
4. **Mobile app** - Convert to Progressive Web App (PWA)
5. **Bulk operations** - Import/export employees, bulk attendance updates

### Integration Options
1. **Barcode scanning** - Use device camera for employee check-ins
2. **Geolocation** - Track attendance location
3. **Notifications** - Email/SMS alerts for attendance events
4. **Calendar integration** - Sync with Google Calendar or Outlook

## 📝 API Examples

### Get All Employees
```javascript
const employees = await odooAPI.searchRead('hr.employee', [], [
    'name', 'barcode', 'work_email', 'department_id'
]);
```

### Record Attendance
```javascript
const attendanceId = await odooAPI.create('hr.attendance', {
    employee_id: employeeId,
    check_in: '2024-01-15 08:00:00'
});
```

### Export Data
```javascript
const exportId = await odooAPI.create('hr.attendance.export', {
    name: 'My Export',
    date_from: '2024-01-01',
    date_to: '2024-01-31'
});

await odooAPI.execute('hr.attendance.export', 'action_export', [exportId]);
```

## 🎉 Enjoy!

You now have a fully functional web frontend that connects to your Odoo attendance system. The interface provides an intuitive way to manage employees and track attendance without needing to use the Odoo web interface directly.

Happy attendance tracking! 🕐✨
