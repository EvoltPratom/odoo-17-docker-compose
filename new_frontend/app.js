/**
 * Main Application JavaScript
 * Handles UI interactions and data management
 */

// Global variables
let employees = [];
let attendances = [];
let locations = [];
let currentFilter = 'today';

// DOM Elements
const loginSection = document.getElementById('loginSection');
const dashboard = document.getElementById('dashboard');
const connectionStatus = document.getElementById('connectionStatus');
const loginForm = document.getElementById('loginForm');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');
    updateConnectionStatus(false);
    setupEventListeners();
    
    // Set current date/time for attendance form
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    const attDateTime = document.getElementById('attDateTime');
    if (attDateTime) {
        attDateTime.value = localDateTime;
    }
});

// Setup event listeners
function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Create employee form
    const createEmployeeForm = document.getElementById('createEmployeeForm');
    if (createEmployeeForm) {
        createEmployeeForm.addEventListener('submit', handleCreateEmployee);
    }

    // Create location form
    const createLocationForm = document.getElementById('createLocationForm');
    if (createLocationForm) {
        createLocationForm.addEventListener('submit', handleCreateLocation);
    }

    // Attendance form
    const attendanceForm = document.getElementById('attendanceForm');
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', handleRecordAttendance);
    }
    
    // Modal close events
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const url = document.getElementById('odooUrl').value;
    const database = document.getElementById('database').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    updateConnectionStatus(false, 'Connecting...');
    
    try {
        const result = await odooAPI.connect(url, database, username, password);
        
        if (result.success) {
            if (result.mockMode) {
                updateConnectionStatus(true, 'Demo Mode');
                showToast('Running in demo mode with sample data', 'info');
            } else {
                updateConnectionStatus(true, 'Connected');
                showToast('Connected to Odoo successfully!', 'success');
            }
            showDashboard();
            await loadInitialData();
        } else {
            updateConnectionStatus(false, 'Connection failed');
            showToast('Connection failed: ' + result.error, 'error');
        }
    } catch (error) {
        updateConnectionStatus(false, 'Connection failed');
        showToast('Connection failed: ' + error.message, 'error');
    }
}

// Update connection status
function updateConnectionStatus(connected, text = null) {
    const indicator = connectionStatus.querySelector('.status-indicator');
    const statusText = connectionStatus.querySelector('.status-text');
    
    if (connected) {
        indicator.classList.add('connected');
        statusText.textContent = text || 'Connected';
    } else {
        indicator.classList.remove('connected');
        statusText.textContent = text || 'Disconnected';
    }
}

// Show dashboard
function showDashboard() {
    loginSection.style.display = 'none';
    dashboard.style.display = 'block';
}

// Load initial data
async function loadInitialData() {
    await Promise.all([
        loadEmployees(),
        loadLocations(),
        loadAttendances(),
        updateStats()
    ]);
}

// Load employees
async function loadEmployees() {
    try {
        console.log('Loading employees...');
        const employeeIds = await odooAPI.search('hr.employee');
        console.log('Employee IDs:', employeeIds);

        employees = await odooAPI.read('hr.employee', employeeIds, [
            'name', 'barcode', 'work_email', 'work_phone', 'department_id', 'job_id', 'active'
        ]);
        console.log('Employees loaded:', employees);

        displayEmployees(employees);
        populateEmployeeSelect();

    } catch (error) {
        console.error('Failed to load employees:', error);
        showToast('Failed to load employees: ' + error.message, 'error');

        // Show empty state
        const employeeListElement = document.getElementById('employeeList');
        employeeListElement.innerHTML = `
            <div class="text-center">
                <p>❌ Failed to load employees</p>
                <p style="font-size: 0.9rem; color: #666;">${error.message}</p>
                <button class="btn btn-primary" onclick="loadEmployees()">
                    <i class="fas fa-retry"></i> Retry
                </button>
            </div>
        `;
    }
}

// Display employees
function displayEmployees(employeeList) {
    const employeeListElement = document.getElementById('employeeList');
    
    if (employeeList.length === 0) {
        employeeListElement.innerHTML = '<div class="text-center">No employees found</div>';
        return;
    }
    
    const html = employeeList.map(employee => `
        <div class="employee-item" onclick="showEmployeeDetails(${employee.id})">
            <div class="employee-avatar">
                ${employee.name.charAt(0).toUpperCase()}
            </div>
            <div class="employee-info">
                <div class="employee-name">${employee.name}</div>
                <div class="employee-details">
                    ${employee.barcode || 'No barcode'} • 
                    ${employee.work_email || 'No email'} • 
                    ${employee.department_id ? employee.department_id[1] : 'No department'}
                </div>
            </div>
            <div class="employee-status ${getEmployeeStatus(employee.id) === 'Present' ? 'status-present' : 'status-absent'}">
                ${getEmployeeStatus(employee.id)}
            </div>
        </div>
    `).join('');
    
    employeeListElement.innerHTML = html;
}

// Get employee status (present/absent)
function getEmployeeStatus(employeeId) {
    const today = new Date().toISOString().split('T')[0];
    const todayAttendance = attendances.filter(att =>
        att.employee_id[0] === employeeId &&
        att.check_in.startsWith(today)
    );

    if (todayAttendance.length === 0) return 'Absent';

    const latestAttendance = todayAttendance[todayAttendance.length - 1];
    return latestAttendance.check_out ? 'Left' : 'Present';
}

// Load locations (departments)
async function loadLocations() {
    try {
        console.log('Loading locations...');
        const locationIds = await odooAPI.search('hr.department');
        console.log('Location IDs:', locationIds);

        locations = await odooAPI.read('hr.department', locationIds, [
            'name', 'complete_name'
        ]);
        console.log('Locations loaded:', locations);

        displayLocations(locations);
        populateLocationSelect();

    } catch (error) {
        console.error('Failed to load locations:', error);
        showToast('Failed to load locations: ' + error.message, 'error');

        // Show empty state
        const locationListElement = document.getElementById('locationList');
        locationListElement.innerHTML = `
            <div class="text-center">
                <p>❌ Failed to load locations</p>
                <p style="font-size: 0.9rem; color: #666;">${error.message}</p>
                <button class="btn btn-primary" onclick="loadLocations()">
                    <i class="fas fa-retry"></i> Retry
                </button>
            </div>
        `;
    }
}

// Display locations
function displayLocations(locationList) {
    const locationListElement = document.getElementById('locationList');

    if (locationList.length === 0) {
        locationListElement.innerHTML = '<div class="text-center">No locations found</div>';
        return;
    }

    const html = locationList.map(location => `
        <div class="location-item" onclick="showLocationDetails(${location.id})">
            <div class="location-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="location-info">
                <div class="location-name">${location.name}</div>
                <div class="location-details">
                    ${location.complete_name || location.name}
                </div>
            </div>
            <div class="location-occupancy">
                ${getLocationOccupancy(location.id)} present
            </div>
        </div>
    `).join('');

    locationListElement.innerHTML = html;
}

// Get location occupancy
function getLocationOccupancy(locationId) {
    const today = new Date().toISOString().split('T')[0];
    const presentEmployees = employees.filter(emp => {
        if (!emp.department_id || emp.department_id[0] !== locationId) return false;

        const todayAttendance = attendances.filter(att =>
            att.employee_id[0] === emp.id &&
            att.check_in.startsWith(today) &&
            !att.check_out
        );

        return todayAttendance.length > 0;
    });

    return presentEmployees.length;
}

// Load attendances
async function loadAttendances() {
    try {
        console.log('Loading attendances...');
        const attendanceIds = await odooAPI.search('hr.attendance');
        console.log('Attendance IDs:', attendanceIds);

        attendances = await odooAPI.read('hr.attendance', attendanceIds, [
            'employee_id', 'check_in', 'check_out', 'worked_hours'
        ]);
        console.log('Attendances loaded:', attendances);

        displayAttendances(attendances);

    } catch (error) {
        console.error('Failed to load attendances:', error);
        showToast('Failed to load attendances: ' + error.message, 'error');

        // Show empty state
        const attendanceListElement = document.getElementById('attendanceList');
        attendanceListElement.innerHTML = `
            <div class="text-center">
                <p>❌ Failed to load attendance records</p>
                <p style="font-size: 0.9rem; color: #666;">${error.message}</p>
                <button class="btn btn-primary" onclick="loadAttendances()">
                    <i class="fas fa-retry"></i> Retry
                </button>
            </div>
        `;
    }
}

// Display attendances
function displayAttendances(attendanceList) {
    const attendanceListElement = document.getElementById('attendanceList');
    
    if (attendanceList.length === 0) {
        attendanceListElement.innerHTML = '<div class="text-center">No attendance records found</div>';
        return;
    }
    
    // Filter attendances based on current filter
    const filteredAttendances = filterAttendancesByPeriod(attendanceList, currentFilter);
    
    // Sort by check_in time (most recent first)
    filteredAttendances.sort((a, b) => new Date(b.check_in) - new Date(a.check_in));
    
    const html = filteredAttendances.slice(0, 20).map(attendance => {
        const checkInTime = new Date(attendance.check_in).toLocaleString();
        const checkOutTime = attendance.check_out ? new Date(attendance.check_out).toLocaleString() : null;
        
        return `
            <div class="attendance-item">
                <div class="attendance-time">${checkInTime.split(' ')[1]}</div>
                <div class="attendance-employee">${attendance.employee_id[1]}</div>
                <div class="attendance-action ${checkOutTime ? 'action-checkout' : 'action-checkin'}">
                    ${checkOutTime ? 'Check Out' : 'Check In'}
                </div>
            </div>
        `;
    }).join('');
    
    attendanceListElement.innerHTML = html;
}

// Filter attendances by period
function filterAttendancesByPeriod(attendanceList, period) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (period) {
        case 'today':
            return attendanceList.filter(att => {
                const checkInDate = new Date(att.check_in);
                return checkInDate >= today;
            });
        case 'week':
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay());
            return attendanceList.filter(att => {
                const checkInDate = new Date(att.check_in);
                return checkInDate >= weekStart;
            });
        case 'month':
            const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
            return attendanceList.filter(att => {
                const checkInDate = new Date(att.check_in);
                return checkInDate >= monthStart;
            });
        default:
            return attendanceList;
    }
}

// Update statistics
async function updateStats() {
    try {
        const totalEmployeesElement = document.getElementById('totalEmployees');
        const presentTodayElement = document.getElementById('presentToday');
        const totalHoursTodayElement = document.getElementById('totalHoursToday');
        const attendanceRecordsElement = document.getElementById('attendanceRecords');
        
        // Total employees
        totalEmployeesElement.textContent = employees.length;
        
        // Present today
        const today = new Date().toISOString().split('T')[0];
        const todayAttendances = attendances.filter(att => att.check_in.startsWith(today));
        const uniqueEmployeesToday = new Set(todayAttendances.map(att => att.employee_id[0]));
        presentTodayElement.textContent = uniqueEmployeesToday.size;
        
        // Total hours today
        const totalHours = todayAttendances.reduce((sum, att) => sum + (att.worked_hours || 0), 0);
        totalHoursTodayElement.textContent = totalHours.toFixed(1) + 'h';
        
        // Attendance records today
        attendanceRecordsElement.textContent = todayAttendances.length;
        
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

// Populate employee select dropdown
function populateEmployeeSelect() {
    const select = document.getElementById('attEmployee');
    if (!select) return;

    select.innerHTML = '<option value="">Select Employee</option>';
    employees.forEach(employee => {
        const option = document.createElement('option');
        option.value = employee.id;
        option.textContent = employee.name;
        select.appendChild(option);
    });
}

// Populate location select dropdown
function populateLocationSelect() {
    const select = document.getElementById('attLocation');
    if (!select) return;

    select.innerHTML = '<option value="">Select Location</option>';
    locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.id;
        option.textContent = location.name;
        select.appendChild(option);
    });
}

// Show employee details modal
function showEmployeeDetails(employeeId) {
    const employee = employees.find(emp => emp.id === employeeId);
    if (!employee) return;
    
    const modal = document.getElementById('employeeModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = employee.name;
    
    // Get employee's recent attendance
    const employeeAttendances = attendances
        .filter(att => att.employee_id[0] === employeeId)
        .sort((a, b) => new Date(b.check_in) - new Date(a.check_in))
        .slice(0, 10);
    
    const attendanceHtml = employeeAttendances.length > 0 ? 
        employeeAttendances.map(att => `
            <div class="attendance-item">
                <div class="attendance-time">${new Date(att.check_in).toLocaleDateString()}</div>
                <div class="attendance-employee">
                    ${new Date(att.check_in).toLocaleTimeString()} - 
                    ${att.check_out ? new Date(att.check_out).toLocaleTimeString() : 'Still working'}
                </div>
                <div class="attendance-action">${att.worked_hours?.toFixed(1) || '0.0'}h</div>
            </div>
        `).join('') : '<p>No attendance records found</p>';
    
    modalBody.innerHTML = `
        <div class="employee-details-modal">
            <div class="form-group">
                <strong>Email:</strong> ${employee.work_email || 'Not set'}
            </div>
            <div class="form-group">
                <strong>Phone:</strong> ${employee.work_phone || 'Not set'}
            </div>
            <div class="form-group">
                <strong>Barcode:</strong> ${employee.barcode || 'Not set'}
            </div>
            <div class="form-group">
                <strong>Department:</strong> ${employee.department_id ? employee.department_id[1] : 'Not assigned'}
            </div>
            <div class="form-group">
                <strong>Job:</strong> ${employee.job_id ? employee.job_id[1] : 'Not assigned'}
            </div>
            <h4>Recent Attendance:</h4>
            <div class="attendance-list">
                ${attendanceHtml}
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Show create employee modal
function showCreateEmployee() {
    const modal = document.getElementById('createEmployeeModal');
    modal.style.display = 'block';
    
    // Clear form
    document.getElementById('createEmployeeForm').reset();
}

// Handle create employee
async function handleCreateEmployee(event) {
    event.preventDefault();
    
    const name = document.getElementById('empName').value;
    const barcode = document.getElementById('empBarcode').value;
    const email = document.getElementById('empEmail').value;
    const phone = document.getElementById('empPhone').value;
    
    try {
        const employeeData = {
            name: name,
            active: true
        };
        
        if (barcode) employeeData.barcode = barcode;
        if (email) employeeData.work_email = email;
        if (phone) employeeData.work_phone = phone;
        
        const newEmployeeId = await odooAPI.create('hr.employee', employeeData);
        
        showToast('Employee created successfully!', 'success');
        closeModal('createEmployeeModal');
        
        // Reload employees
        await loadEmployees();
        await updateStats();
        
    } catch (error) {
        console.error('Failed to create employee:', error);
        showToast('Failed to create employee: ' + error.message, 'error');
    }
}

// Show create location modal
function showCreateLocation() {
    const modal = document.getElementById('createLocationModal');
    modal.style.display = 'block';

    // Clear form
    document.getElementById('createLocationForm').reset();
}

// Handle create location
async function handleCreateLocation(event) {
    event.preventDefault();

    const name = document.getElementById('locName').value;
    const building = document.getElementById('locBuilding').value;
    const capacity = document.getElementById('locCapacity').value;

    try {
        const locationData = {
            name: name,
            complete_name: building ? `${building} / ${name}` : name
        };

        const newLocationId = await odooAPI.create('hr.department', locationData);

        showToast('Location created successfully!', 'success');
        closeModal('createLocationModal');

        // Reload locations
        await loadLocations();

    } catch (error) {
        console.error('Failed to create location:', error);
        showToast('Failed to create location: ' + error.message, 'error');
    }
}

// Show location details modal
function showLocationDetails(locationId) {
    const location = locations.find(loc => loc.id === locationId);
    if (!location) return;

    const modal = document.getElementById('employeeModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = location.name;

    // Get employees in this location
    const locationEmployees = employees.filter(emp =>
        emp.department_id && emp.department_id[0] === locationId
    );

    const employeeHtml = locationEmployees.length > 0 ?
        locationEmployees.map(emp => `
            <div class="employee-item">
                <div class="employee-name">${emp.name}</div>
                <div class="employee-status">${getEmployeeStatus(emp.id)}</div>
            </div>
        `).join('') : '<p>No employees assigned to this location</p>';

    modalBody.innerHTML = `
        <div class="location-details-modal">
            <div class="form-group">
                <strong>Full Name:</strong> ${location.complete_name || location.name}
            </div>
            <div class="form-group">
                <strong>Current Occupancy:</strong> ${getLocationOccupancy(locationId)} people present
            </div>
            <h4>Employees in this Location:</h4>
            <div class="employee-list">
                ${employeeHtml}
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

// Show attendance form modal
function showAttendanceForm() {
    const modal = document.getElementById('attendanceModal');
    modal.style.display = 'block';
    
    // Set current date/time
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    document.getElementById('attDateTime').value = localDateTime;
}

// Handle record attendance
async function handleRecordAttendance(event) {
    event.preventDefault();

    const employeeId = parseInt(document.getElementById('attEmployee').value);
    const locationId = parseInt(document.getElementById('attLocation').value);
    const type = document.getElementById('attType').value;
    const dateTime = document.getElementById('attDateTime').value;
    
    try {
        if (type === 'checkin') {
            const attendanceData = {
                employee_id: employeeId,
                check_in: dateTime.replace('T', ' ') + ':00'
            };
            
            await odooAPI.create('hr.attendance', attendanceData);
            showToast('Check-in recorded successfully!', 'success');
            
        } else if (type === 'checkout') {
            // Find the latest check-in without check-out for this employee
            const openAttendance = attendances.find(att => 
                att.employee_id[0] === employeeId && !att.check_out
            );
            
            if (openAttendance) {
                await odooAPI.write('hr.attendance', [openAttendance.id], {
                    check_out: dateTime.replace('T', ' ') + ':00'
                });
                showToast('Check-out recorded successfully!', 'success');
            } else {
                showToast('No open check-in found for this employee', 'error');
                return;
            }
        }
        
        closeModal('attendanceModal');
        
        // Reload data
        await loadAttendances();
        await updateStats();
        
    } catch (error) {
        console.error('Failed to record attendance:', error);
        showToast('Failed to record attendance: ' + error.message, 'error');
    }
}

// Filter functions
function filterEmployees() {
    const searchTerm = document.getElementById('employeeSearch').value.toLowerCase();
    const filteredEmployees = employees.filter(emp => 
        emp.name.toLowerCase().includes(searchTerm) ||
        (emp.work_email && emp.work_email.toLowerCase().includes(searchTerm)) ||
        (emp.barcode && emp.barcode.toLowerCase().includes(searchTerm))
    );
    displayEmployees(filteredEmployees);
}

function filterAttendance() {
    currentFilter = document.getElementById('attendanceFilter').value;
    displayAttendances(attendances);
}

// Refresh data
async function refreshData() {
    showToast('Refreshing data...', 'info');
    await loadInitialData();
    showToast('Data refreshed successfully!', 'success');
}

// Export attendance
async function exportAttendance() {
    try {
        showToast('Creating export...', 'info');

        // Try the custom export module first
        try {
            const exportConfig = {
                name: `Web Export ${new Date().toISOString().split('T')[0]}`,
                export_path: '/tmp/attendance_exports',
                date_from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                date_to: new Date().toISOString().split('T')[0],
                auto_export: false
            };

            const exportId = await odooAPI.create('hr.attendance.export', exportConfig);
            const result = await odooAPI.execute('hr.attendance.export', 'action_export', [exportId]);

            showToast('Export created successfully!', 'success');

        } catch (customExportError) {
            console.warn('Custom export module not available, using basic export:', customExportError.message);

            // Fall back to basic export - just get the data and show it
            await basicExport();
        }

    } catch (error) {
        console.error('Failed to export attendance:', error);
        showToast('Export failed: ' + error.message, 'error');
    }
}

// Basic export function when custom module is not available
async function basicExport() {
    try {
        // Get attendance data for the last 30 days
        const dateFrom = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        const dateTo = new Date();

        // Search for attendance records in date range
        const domain = [
            ['check_in', '>=', dateFrom.toISOString().split('T')[0] + ' 00:00:00'],
            ['check_in', '<=', dateTo.toISOString().split('T')[0] + ' 23:59:59']
        ];

        const attendanceIds = await odooAPI.search('hr.attendance', domain);

        if (attendanceIds.length === 0) {
            showToast('No attendance records found for export', 'info');
            return;
        }

        const attendanceData = await odooAPI.read('hr.attendance', attendanceIds, [
            'employee_id', 'check_in', 'check_out', 'worked_hours'
        ]);

        // Create export data structure
        const exportData = {
            export_info: {
                export_name: `Basic Export ${new Date().toISOString().split('T')[0]}`,
                export_date: new Date().toISOString(),
                date_from: dateFrom.toISOString().split('T')[0],
                date_to: dateTo.toISOString().split('T')[0],
                total_records: attendanceData.length,
                exported_by: 'Web Frontend'
            },
            attendance_records: attendanceData.map(record => ({
                id: record.id,
                employee_id: record.employee_id[0],
                employee_name: record.employee_id[1],
                check_in: record.check_in,
                check_out: record.check_out,
                worked_hours: record.worked_hours
            }))
        };

        // Download as JSON file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `attendance_export_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast(`Exported ${attendanceData.length} attendance records!`, 'success');

    } catch (error) {
        console.error('Basic export failed:', error);
        showToast('Basic export failed: ' + error.message, 'error');
    }
}

// Utility functions
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
