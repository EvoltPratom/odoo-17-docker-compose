/**
 * Odoo API Wrapper - Handles all communication with Odoo backend
 */

class OdooAPI {
    constructor() {
        this.config = {
            url: 'http://localhost:10017',
            database: localStorage.getItem('odoo_db') || 'attendance_demo',
            username: localStorage.getItem('odoo_user') || 'admin',
            password: localStorage.getItem('odoo_pass') || 'admin'
        };
        this.uid = null;
        this.isAuthenticated = false;
    }

    // Update configuration
    updateConfig(database, username, password) {
        this.config.database = database;
        this.config.username = username;
        this.config.password = password;
        
        // Store in localStorage
        localStorage.setItem('odoo_db', database);
        localStorage.setItem('odoo_user', username);
        localStorage.setItem('odoo_pass', password);
    }

    // Authenticate with Odoo
    async authenticate() {
        try {
            const response = await fetch(`${this.config.url}/web/session/authenticate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        db: this.config.database,
                        login: this.config.username,
                        password: this.config.password
                    }
                })
            });

            const data = await response.json();
            
            if (data.result && data.result.uid) {
                this.uid = data.result.uid;
                this.isAuthenticated = true;
                return true;
            }
            
            this.isAuthenticated = false;
            return false;
        } catch (error) {
            console.error('Authentication error:', error);
            this.isAuthenticated = false;
            return false;
        }
    }

    // Generic API call to Odoo
    async call(model, method, args = [], kwargs = {}) {
        if (!this.isAuthenticated) {
            throw new Error('Not authenticated. Please authenticate first.');
        }

        try {
            const response = await fetch(`${this.config.url}/web/dataset/call_kw`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        model: model,
                        method: method,
                        args: args,
                        kwargs: kwargs
                    }
                })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error.message || 'API call failed');
            }
            
            return data.result;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }

    // Employee methods
    async getEmployees() {
        return await this.call('hr.employee', 'search_read', [], {
            fields: ['id', 'name', 'barcode', 'work_email', 'department_id', 'job_id']
        });
    }

    async createEmployee(employeeData) {
        return await this.call('hr.employee', 'create', [employeeData]);
    }

    async getEmployee(employeeId) {
        const result = await this.call('hr.employee', 'read', [employeeId], {
            fields: ['id', 'name', 'barcode', 'work_email', 'department_id', 'job_id']
        });
        return result[0];
    }

    // Attendance methods
    async getAttendanceRecords(limit = 20, employeeId = null) {
        let domain = [];
        if (employeeId) {
            domain.push(['employee_id', '=', employeeId]);
        }

        return await this.call('hr.attendance', 'search_read', [domain], {
            fields: ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours'],
            order: 'check_in desc',
            limit: limit
        });
    }

    async clockIn(employeeId) {
        return await this.call('hr.attendance', 'create', [{
            employee_id: employeeId,
            check_in: new Date().toISOString().replace('T', ' ').substring(0, 19)
        }]);
    }

    async clockOut(employeeId) {
        // Find the last attendance record for this employee without check_out
        const openAttendance = await this.call('hr.attendance', 'search_read', [
            [
                ['employee_id', '=', employeeId],
                ['check_out', '=', false]
            ]
        ], {
            fields: ['id'],
            order: 'check_in desc',
            limit: 1
        });

        if (openAttendance.length === 0) {
            throw new Error('No open attendance record found. Please clock in first.');
        }

        return await this.call('hr.attendance', 'write', [
            [openAttendance[0].id],
            {
                check_out: new Date().toISOString().replace('T', ' ').substring(0, 19)
            }
        ]);
    }

    async getEmployeeCurrentStatus(employeeId) {
        const openAttendance = await this.call('hr.attendance', 'search_read', [
            [
                ['employee_id', '=', employeeId],
                ['check_out', '=', false]
            ]
        ], {
            fields: ['id', 'check_in'],
            order: 'check_in desc',
            limit: 1
        });

        return openAttendance.length > 0 ? {
            status: 'clocked_in',
            since: openAttendance[0].check_in
        } : {
            status: 'clocked_out',
            since: null
        };
    }

    // Export methods
    async exportAttendance(dateFrom, dateTo, employeeIds = []) {
        const exportConfig = {
            name: `Export ${new Date().toLocaleDateString()}`,
            export_path: '/tmp/attendance_exports',
            date_from: dateFrom,
            date_to: dateTo,
            auto_export: false
        };

        if (employeeIds.length > 0) {
            exportConfig.employee_ids = [[6, 0, employeeIds]];
        }

        const exportId = await this.call('hr.attendance.export', 'create', [exportConfig]);
        return await this.call('hr.attendance.export', 'action_export', [exportId]);
    }

    // Generate report data
    async generateAttendanceReport(dateFrom, dateTo, employeeId = null) {
        let domain = [
            ['check_in', '>=', dateFrom],
            ['check_in', '<=', dateTo]
        ];

        if (employeeId) {
            domain.push(['employee_id', '=', employeeId]);
        }

        const records = await this.call('hr.attendance', 'search_read', [domain], {
            fields: ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']
        });

        // Process report data
        const reportData = {
            total_records: records.length,
            total_hours: records.reduce((sum, record) => sum + (record.worked_hours || 0), 0),
            employees: {}
        };

        records.forEach(record => {
            const empId = record.employee_id[0];
            const empName = record.employee_id[1];
            
            if (!reportData.employees[empId]) {
                reportData.employees[empId] = {
                    name: empName,
                    total_hours: 0,
                    total_days: 0,
                    records: []
                };
            }
            
            reportData.employees[empId].total_hours += record.worked_hours || 0;
            reportData.employees[empId].total_days += 1;
            reportData.employees[empId].records.push(record);
        });

        return reportData;
    }

    // Utility methods
    formatDateTime(dateTimeString) {
        return new Date(dateTimeString).toLocaleString();
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    formatTime(dateTimeString) {
        return new Date(dateTimeString).toLocaleTimeString();
    }

    formatHours(hours) {
        return hours ? hours.toFixed(2) : '0.00';
    }
}

// Create global instance
const odooAPI = new OdooAPI();
