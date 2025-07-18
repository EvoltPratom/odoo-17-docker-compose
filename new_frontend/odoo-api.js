/**
 * Odoo API Client for Web Frontend
 * Handles all communication with Odoo XML-RPC API
 */

class OdooAPI {
    constructor() {
        this.url = '';
        this.db = '';
        this.username = '';
        this.password = '';
        this.uid = null;
        this.isConnected = false;
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

            console.log('Connecting to Odoo...', { url, db, username });

            // Try to make request to our proxy server
            try {
                console.log('Attempting to connect via proxy server...');
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url, db, username, password })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                console.log('Proxy server response:', result);

                if (result.success) {
                    this.uid = result.uid;
                    this.isConnected = true;
                    this.useMockData = false;
                    console.log('Connected successfully to real Odoo, UID:', this.uid);
                    return { success: true, uid: this.uid };
                } else {
                    throw new Error(result.error);
                }
            } catch (fetchError) {
                console.warn('Proxy server not available, using mock data:', fetchError.message);
                console.log('This is normal if you\'re using the simple server');
                // Fall back to mock data
                this.uid = 1;
                this.isConnected = true;
                this.useMockData = true;
                console.log('Using mock data mode');
                return { success: true, uid: this.uid, mockMode: true };
            }

        } catch (error) {
            console.error('Connection failed:', error);
            this.isConnected = false;
            return { success: false, error: error.message };
        }
    }

    /**
     * Check if connected to Odoo
     */
    isAuthenticated() {
        return this.isConnected && this.uid;
    }

    /**
     * Make a call to Odoo API
     */
    async call(model, method, args = [], kwargs = {}) {
        if (!this.isAuthenticated()) {
            throw new Error('Not authenticated');
        }

        try {
            console.log('API Call:', { model, method, args, kwargs });

            // If using mock data, return mock results
            if (this.useMockData) {
                await new Promise(resolve => setTimeout(resolve, 300)); // Simulate delay
                return this.getMockData(model, method, args, kwargs);
            }

            // Make request to our proxy server
            const response = await fetch('/api/call', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model, method, args, kwargs })
            });

            const result = await response.json();

            if (result.success) {
                return result.result;
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }



    /**
     * Get mock data for demonstration when proxy server is not available
     */
    getMockData(model, method, args, kwargs) {
        const mockData = {
            'hr.employee': {
                'search': [1, 2, 3, 4],
                'read': [
                    {
                        id: 1,
                        name: 'Alice Johnson',
                        barcode: 'DEMO001',
                        work_email: 'alice@demo.com',
                        work_phone: '+1-555-0101',
                        department_id: [1, 'Sales'],
                        job_id: [1, 'Sales Representative'],
                        active: true
                    },
                    {
                        id: 2,
                        name: 'Bob Smith',
                        barcode: 'DEMO002',
                        work_email: 'bob@demo.com',
                        work_phone: '+1-555-0102',
                        department_id: [2, 'Engineering'],
                        job_id: [2, 'Software Developer'],
                        active: true
                    },
                    {
                        id: 3,
                        name: 'Carol Davis',
                        barcode: 'DEMO003',
                        work_email: 'carol@demo.com',
                        work_phone: '+1-555-0103',
                        department_id: [3, 'HR'],
                        job_id: [3, 'HR Manager'],
                        active: true
                    },
                    {
                        id: 4,
                        name: 'David Wilson',
                        barcode: 'DEMO004',
                        work_email: 'david@demo.com',
                        work_phone: '+1-555-0104',
                        department_id: [2, 'Engineering'],
                        job_id: [4, 'Senior Developer'],
                        active: true
                    }
                ],
                'create': Math.floor(Math.random() * 1000) + 5
            },
            'hr.attendance': {
                'search': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'read': [
                    {
                        id: 1,
                        employee_id: [1, 'Alice Johnson'],
                        check_in: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        check_out: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        worked_hours: 7.0
                    },
                    {
                        id: 2,
                        employee_id: [2, 'Bob Smith'],
                        check_in: new Date(Date.now() - 7 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        check_out: null,
                        worked_hours: 0.0
                    },
                    {
                        id: 3,
                        employee_id: [3, 'Carol Davis'],
                        check_in: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        check_out: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        worked_hours: 4.0
                    },
                    {
                        id: 4,
                        employee_id: [4, 'David Wilson'],
                        check_in: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19),
                        check_out: null,
                        worked_hours: 0.0
                    }
                ],
                'create': Math.floor(Math.random() * 1000) + 10
            },
            'hr.attendance.export': {
                'search': [],
                'read': [],
                'create': null,
                'action_export': null
            }
        };

        if (method === 'search') {
            return mockData[model]?.[method] || [];
        } else if (method === 'read') {
            const ids = args[0] || [];
            const allRecords = mockData[model]?.[method] || [];
            if (ids.length === 0) {
                return allRecords;
            }
            return allRecords.filter(record => ids.includes(record.id));
        } else if (method === 'create') {
            return mockData[model]?.[method] || Math.floor(Math.random() * 1000) + 1;
        } else if (method === 'write') {
            return true;
        } else if (method === 'unlink') {
            return true;
        } else if (method.startsWith('action_')) {
            return mockData[model]?.[method] || { success: true };
        }

        return mockData[model]?.[method] || null;
    }

    /**
     * Search for records
     */
    async search(model, domain = [], options = {}) {
        return await this.call(model, 'search', [domain], options);
    }

    /**
     * Read records
     */
    async read(model, ids, fields = []) {
        const options = fields.length > 0 ? { fields } : {};
        return await this.call(model, 'read', [ids], options);
    }

    /**
     * Search and read records in one call
     */
    async searchRead(model, domain = [], fields = [], options = {}) {
        const ids = await this.search(model, domain, options);
        if (ids.length === 0) return [];
        return await this.read(model, ids, fields);
    }

    /**
     * Create a new record
     */
    async create(model, values) {
        return await this.call(model, 'create', [values]);
    }

    /**
     * Update existing records
     */
    async write(model, ids, values) {
        return await this.call(model, 'write', [ids, values]);
    }

    /**
     * Delete records
     */
    async unlink(model, ids) {
        return await this.call(model, 'unlink', [ids]);
    }

    /**
     * Execute a method on a model
     */
    async execute(model, method, ids, ...args) {
        return await this.call(model, method, [ids, ...args]);
    }
}

// Create global instance
window.odooAPI = new OdooAPI();
