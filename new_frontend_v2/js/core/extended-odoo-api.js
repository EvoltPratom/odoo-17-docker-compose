/**
 * Extended Odoo API Client for Extended Attendance System
 * Handles all communication with the new extended attendance backend
 */

class ExtendedOdooAPI {
    constructor() {
        this.url = '';
        this.db = '';
        this.username = '';
        this.password = '';
        this.uid = null;
        this.isConnected = false;
        this.sessionId = null;
        this.useMockData = false;
    }

    /**
     * Connect to Odoo and authenticate
     */
    async connect(url, db, username, password) {
        try {
            this.url = url;
            this.db = db;
            this.username = username;
            this.password = password;

            console.log('Connecting to Extended Attendance System...', { url, db, username });

            // Try to connect via proxy server first
            try {
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, db, username, password })
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        this.uid = result.uid;
                        this.sessionId = result.session_id;
                        this.isConnected = true;
                        this.useMockData = false;
                        console.log('Connected to real Odoo successfully, UID:', this.uid);
                        return { success: true, uid: this.uid };
                    }
                }
            } catch (proxyError) {
                console.log('Proxy connection failed, falling back to mock data');
            }

            // Fallback to mock data
            console.log('Using mock data for development');
            this.useMockData = true;
            this.isConnected = true;
            this.uid = 1;
            return { success: true, uid: this.uid, mock: true };

        } catch (error) {
            console.error('Connection failed:', error);
            throw new Error(`Failed to connect: ${error.message}`);
        }
    }

    /**
     * Make API call to extended attendance endpoints
     */
    async apiCall(endpoint, method = 'GET', data = null) {
        if (this.useMockData) {
            return this._mockApiCall(endpoint, method, data);
        }

        try {
            const url = `${this.url}${endpoint}`;
            const requestData = {
                jsonrpc: "2.0",
                method: "call",
                params: data || {},
                id: Date.now()
            };

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error.message || 'API call failed');
            }

            return result.result;
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // ==================== PERSON TYPES API ====================

    async getPersonTypes() {
        return await this.apiCall('/api/attendance/person-types');
    }

    async createPersonType(data) {
        return await this.apiCall('/api/attendance/person-types', 'POST', data);
    }

    async updatePersonType(id, data) {
        return await this.apiCall(`/api/attendance/person-types/${id}`, 'PUT', data);
    }

    async deletePersonType(id) {
        return await this.apiCall(`/api/attendance/person-types/${id}`, 'DELETE');
    }

    // ==================== LOCATIONS API ====================

    async getLocations() {
        return await this.apiCall('/api/attendance/locations');
    }

    async createLocation(data) {
        return await this.apiCall('/api/attendance/locations', 'POST', data);
    }

    async updateLocation(id, data) {
        return await this.apiCall(`/api/attendance/locations/${id}`, 'PUT', data);
    }

    async deleteLocation(id) {
        return await this.apiCall(`/api/attendance/locations/${id}`, 'DELETE');
    }

    // ==================== PERSONS API ====================

    async getPersons(filters = {}) {
        return await this.apiCall('/api/attendance/persons', 'GET', filters);
    }

    async createPerson(data) {
        return await this.apiCall('/api/attendance/persons', 'POST', data);
    }

    async updatePerson(id, data) {
        return await this.apiCall(`/api/attendance/persons/${id}`, 'PUT', data);
    }

    async deletePerson(id) {
        return await this.apiCall(`/api/attendance/persons/${id}`, 'DELETE');
    }

    async searchPerson(identifier) {
        return await this.apiCall('/api/attendance/persons/search', 'POST', { identifier });
    }

    // ==================== ATTENDANCE API ====================

    async checkIn(personIdentifier, locationCode, deviceId = null, checkInTime = null) {
        return await this.apiCall('/api/attendance/check-in', 'POST', {
            person_identifier: personIdentifier,
            location_code: locationCode,
            device_id: deviceId,
            check_in_time: checkInTime
        });
    }

    async checkOut(personIdentifier, checkOutTime = null) {
        return await this.apiCall('/api/attendance/check-out', 'POST', {
            person_identifier: personIdentifier,
            check_out_time: checkOutTime
        });
    }

    async getCurrentAttendance(locationCode = null) {
        const params = locationCode ? { location_code: locationCode } : {};
        return await this.apiCall('/api/attendance/current', 'GET', params);
    }

    async getAttendanceRecords(filters = {}) {
        return await this.apiCall('/api/attendance/records', 'GET', filters);
    }

    async generateReport(dateFrom, dateTo, locationCode = null, personTypeCode = null) {
        return await this.apiCall('/api/attendance/report', 'POST', {
            date_from: dateFrom,
            date_to: dateTo,
            location_code: locationCode,
            person_type_code: personTypeCode
        });
    }

    // ==================== MOCK DATA FOR DEVELOPMENT ====================

    _mockApiCall(endpoint, method, data) {
        console.log(`Mock API call: ${method} ${endpoint}`, data);
        
        // Simulate API delay
        return new Promise(resolve => {
            setTimeout(() => {
                resolve(this._getMockResponse(endpoint, method, data));
            }, 300);
        });
    }

    _getMockResponse(endpoint, method, data) {
        const mockData = {
            '/api/attendance/person-types': {
                success: true,
                data: [
                    { id: 1, name: 'Administrator', code: 'ADMIN', is_system: true, person_count: 2, default_access_level: 'full' },
                    { id: 2, name: 'Employee', code: 'EMP', is_system: false, person_count: 15, default_access_level: 'standard' },
                    { id: 3, name: 'Student', code: 'STU', is_system: false, person_count: 150, default_access_level: 'basic' },
                    { id: 4, name: 'Guest', code: 'GST', is_system: false, person_count: 5, default_access_level: 'restricted' }
                ]
            },
            '/api/attendance/locations': {
                success: true,
                data: [
                    { id: 1, name: 'Main Entrance', code: 'MAIN_ENT', current_occupancy: 0, capacity: 0, building: 'Main Building' },
                    { id: 2, name: 'Reception', code: 'RECEPTION', current_occupancy: 2, capacity: 10, building: 'Main Building' },
                    { id: 3, name: 'Library', code: 'LIBRARY', current_occupancy: 25, capacity: 50, building: 'Academic Building' },
                    { id: 4, name: 'Classroom 101', code: 'CLASS_101', current_occupancy: 30, capacity: 35, building: 'Academic Building' },
                    { id: 5, name: 'Science Lab', code: 'SCI_LAB', current_occupancy: 15, capacity: 25, building: 'Science Building' }
                ]
            },
            '/api/attendance/persons': {
                success: true,
                data: [
                    { id: 1, name: 'John Admin', person_id: 'ADMIN001', person_type: { name: 'Administrator', code: 'ADMIN' }, is_checked_in: true, current_location: { name: 'Reception', code: 'RECEPTION' } },
                    { id: 2, name: 'Alice Johnson', person_id: 'EMP001', person_type: { name: 'Employee', code: 'EMP' }, is_checked_in: true, current_location: { name: 'Library', code: 'LIBRARY' } },
                    { id: 3, name: 'Bob Smith', person_id: 'EMP002', person_type: { name: 'Employee', code: 'EMP' }, is_checked_in: false, current_location: null },
                    { id: 4, name: 'Charlie Brown', person_id: 'STU001', person_type: { name: 'Student', code: 'STU' }, is_checked_in: true, current_location: { name: 'Classroom 101', code: 'CLASS_101' } },
                    { id: 5, name: 'Diana Prince', person_id: 'STU002', person_type: { name: 'Student', code: 'STU' }, is_checked_in: true, current_location: { name: 'Science Lab', code: 'SCI_LAB' } }
                ]
            },
            '/api/attendance/current': {
                success: true,
                data: [
                    { id: 1, person_name: 'John Admin', location_name: 'Reception', check_in: '2024-01-15T08:00:00', duration_display: '2h 30m (ongoing)' },
                    { id: 2, person_name: 'Alice Johnson', location_name: 'Library', check_in: '2024-01-15T08:15:00', duration_display: '2h 15m (ongoing)' },
                    { id: 3, person_name: 'Charlie Brown', location_name: 'Classroom 101', check_in: '2024-01-15T09:00:00', duration_display: '1h 30m (ongoing)' },
                    { id: 4, person_name: 'Diana Prince', location_name: 'Science Lab', check_in: '2024-01-15T09:30:00', duration_display: '1h (ongoing)' }
                ]
            }
        };

        if (method === 'POST' && endpoint.includes('check-in')) {
            return { success: true, message: `Successfully checked in ${data.person_identifier} at ${data.location_code}` };
        }

        if (method === 'POST' && endpoint.includes('check-out')) {
            return { success: true, message: `Successfully checked out ${data.person_identifier}` };
        }

        return mockData[endpoint] || { success: true, data: [] };
    }
}

// Export for use in other modules
window.ExtendedOdooAPI = ExtendedOdooAPI;
