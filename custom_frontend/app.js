/**
 * Main Application Logic
 */

let currentEmployee = null;

// Utility function to show messages
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="${type}">${message}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 5000);
}

// Update current time
function updateCurrentTime() {
    const now = new Date();
    document.getElementById('currentTime').textContent = now.toLocaleTimeString();
}

// Load employees
async function loadEmployees() {
    try {
        const employees = await odooAPI.getEmployees();
        const select = document.getElementById('employeeSelect');
        select.innerHTML = '<option value="">Select an employee</option>';
        
        employees.forEach(employee => {
            const option = document.createElement('option');
            option.value = employee.id;
            option.textContent = `${employee.name} ${employee.barcode ? '(' + employee.barcode + ')' : ''}`;
            select.appendChild(option);
        });
    } catch (error) {
        showMessage('Error loading employees: ' + error.message, 'error');
    }
}

// Handle employee selection change
async function onEmployeeChange() {
    const employeeId = document.getElementById('employeeSelect').value;
    const employeeInfo = document.getElementById('employeeInfo');
    const currentStatus = document.getElementById('currentStatus');
    
    if (!employeeId) {
        employeeInfo.innerHTML = '';
        currentStatus.innerHTML = '';
        currentEmployee = null;
        return;
    }

    try {
        // Get employee details
        const employee = await odooAPI.getEmployee(parseInt(employeeId));
        currentEmployee = employee;
        
        // Display employee info
        employeeInfo.innerHTML = `
            <div><strong>Name:</strong> ${employee.name}</div>
            <div><strong>Code:</strong> ${employee.barcode || 'N/A'}</div>
            <div><strong>Email:</strong> ${employee.work_email || 'N/A'}</div>
            <div><strong>Department:</strong> ${employee.department_id ? employee.department_id[1] : 'N/A'}</div>
            <div><strong>Job:</strong> ${employee.job_id ? employee.job_id[1] : 'N/A'}</div>
        `;
        
        // Get current status
        const status = await odooAPI.getEmployeeCurrentStatus(parseInt(employeeId));
        
        if (status.status === 'clocked_in') {
            currentStatus.innerHTML = `
                <span style="color: #28a745;">🟢 Clocked In</span>
                <div style="font-size: 0.9em; color: #666;">Since: ${odooAPI.formatDateTime(status.since)}</div>
            `;
        } else {
            currentStatus.innerHTML = `
                <span style="color: #dc3545;">🔴 Clocked Out</span>
            `;
        }
        
    } catch (error) {
        showMessage('Error loading employee details: ' + error.message, 'error');
    }
}

// Load attendance records
async function loadAttendance() {
    try {
        const attendance = await odooAPI.getAttendanceRecords(15);
        const listDiv = document.getElementById('attendanceList');
        
        if (attendance.length === 0) {
            listDiv.innerHTML = '<div class="loading">No attendance records found</div>';
            return;
        }

        listDiv.innerHTML = '';
        
        attendance.forEach(record => {
            const card = document.createElement('div');
            card.className = 'attendance-card';
            
            const status = record.check_out ? 'out' : 'in';
            const statusText = record.check_out ? 'Clocked Out' : 'Clocked In';
            const statusColor = record.check_out ? '#dc3545' : '#28a745';
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: ${statusColor}; font-weight: bold;">●</span>
                        <strong>${record.employee_id[1]}</strong> - ${statusText}
                    </div>
                    <div style="font-size: 0.9em; color: #666;">
                        ${record.worked_hours ? odooAPI.formatHours(record.worked_hours) + ' hrs' : ''}
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 14px; color: #666;">
                    <div>📅 Check In: ${odooAPI.formatDateTime(record.check_in)}</div>
                    ${record.check_out ? `<div>📅 Check Out: ${odooAPI.formatDateTime(record.check_out)}</div>` : ''}
                </div>
            `;
            
            listDiv.appendChild(card);
        });
    } catch (error) {
        showMessage('Error loading attendance: ' + error.message, 'error');
    }
}

// Clock In
async function clockIn() {
    const employeeId = document.getElementById('employeeSelect').value;
    
    if (!employeeId) {
        showMessage('Please select an employee first', 'error');
        return;
    }

    try {
        await odooAPI.clockIn(parseInt(employeeId));
        showMessage('Successfully clocked in!', 'success');
        
        // Refresh data
        await loadAttendance();
        await onEmployeeChange();
    } catch (error) {
        showMessage('Error clocking in: ' + error.message, 'error');
    }
}

// Clock Out
async function clockOut() {
    const employeeId = document.getElementById('employeeSelect').value;
    
    if (!employeeId) {
        showMessage('Please select an employee first', 'error');
        return;
    }

    try {
        await odooAPI.clockOut(parseInt(employeeId));
        showMessage('Successfully clocked out!', 'success');
        
        // Refresh data
        await loadAttendance();
        await onEmployeeChange();
    } catch (error) {
        showMessage('Error clocking out: ' + error.message, 'error');
    }
}

// Export attendance data
async function exportAttendance() {
    const dateFrom = document.getElementById('exportDateFrom').value;
    const dateTo = document.getElementById('exportDateTo').value;
    
    if (!dateFrom || !dateTo) {
        showMessage('Please select both from and to dates', 'error');
        return;
    }

    try {
        await odooAPI.exportAttendance(dateFrom, dateTo);
        showMessage('Attendance data exported successfully!', 'success');
    } catch (error) {
        showMessage('Error exporting attendance: ' + error.message, 'error');
    }
}

// Generate report
async function generateReport() {
    const dateFrom = document.getElementById('exportDateFrom').value;
    const dateTo = document.getElementById('exportDateTo').value;
    
    if (!dateFrom || !dateTo) {
        showMessage('Please select both from and to dates', 'error');
        return;
    }

    try {
        const reportData = await odooAPI.generateAttendanceReport(dateFrom, dateTo);
        displayReport(reportData);
    } catch (error) {
        showMessage('Error generating report: ' + error.message, 'error');
    }
}

// Display report
function displayReport(reportData) {
    const reportHtml = `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h3>📊 Attendance Report</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    <h4 style="margin: 0; color: #4a90e2;">Total Records</h4>
                    <div style="font-size: 2em; font-weight: bold;">${reportData.total_records}</div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    <h4 style="margin: 0; color: #28a745;">Total Hours</h4>
                    <div style="font-size: 2em; font-weight: bold;">${reportData.total_hours.toFixed(2)}</div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    <h4 style="margin: 0; color: #dc3545;">Employees</h4>
                    <div style="font-size: 2em; font-weight: bold;">${Object.keys(reportData.employees).length}</div>
                </div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 5px;">
                <h4>Employee Details:</h4>
                ${Object.values(reportData.employees).map(emp => `
                    <div style="margin: 10px 0; padding: 10px; border-left: 4px solid #4a90e2; background: #f8f9fa;">
                        <strong>${emp.name}</strong><br>
                        Hours: ${emp.total_hours.toFixed(2)} | Days: ${emp.total_days}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    const exportCard = document.querySelector('.export-card .card-content');
    exportCard.innerHTML += reportHtml;
}

// Settings panel
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    
    // Load current settings
    document.getElementById('dbName').value = odooAPI.config.database;
    document.getElementById('adminUser').value = odooAPI.config.username;
    document.getElementById('adminPass').value = odooAPI.config.password;
}

// Save settings
function saveSettings() {
    const database = document.getElementById('dbName').value;
    const username = document.getElementById('adminUser').value;
    const password = document.getElementById('adminPass').value;
    
    if (!database || !username || !password) {
        showMessage('Please fill in all settings fields', 'error');
        return;
    }
    
    odooAPI.updateConfig(database, username, password);
    showMessage('Settings saved! Please refresh to reconnect.', 'success');
    toggleSettings();
}

// Employee modal functions
function addEmployee() {
    document.getElementById('employeeModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('employeeModal').style.display = 'none';
    document.getElementById('employeeForm').reset();
}

async function saveEmployee() {
    const name = document.getElementById('empName').value;
    const code = document.getElementById('empCode').value;
    const email = document.getElementById('empEmail').value;
    const department = document.getElementById('empDepartment').value;
    
    if (!name) {
        showMessage('Employee name is required', 'error');
        return;
    }
    
    try {
        const employeeData = {
            name: name,
            barcode: code,
            work_email: email
        };
        
        await odooAPI.createEmployee(employeeData);
        showMessage('Employee created successfully!', 'success');
        closeModal();
        await loadEmployees();
    } catch (error) {
        showMessage('Error creating employee: ' + error.message, 'error');
    }
}

// Initialize default date range
function initializeDateRange() {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    document.getElementById('exportDateFrom').value = thirtyDaysAgo.toISOString().split('T')[0];
    document.getElementById('exportDateTo').value = today.toISOString().split('T')[0];
}

// Initialize the application
async function init() {
    showMessage('Connecting to Odoo...', 'info');
    
    // Start time updates
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Initialize date range
    initializeDateRange();
    
    // Authenticate
    const authenticated = await odooAPI.authenticate();
    
    if (!authenticated) {
        showMessage('Failed to connect to Odoo. Please check your settings.', 'error');
        return;
    }

    showMessage('Connected successfully!', 'success');
    
    // Load initial data
    await loadEmployees();
    await loadAttendance();
}

// Start the application when page loads
document.addEventListener('DOMContentLoaded', init);

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('employeeModal');
    if (event.target == modal) {
        closeModal();
    }
}
