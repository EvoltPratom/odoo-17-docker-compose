/**
 * Reports Component
 * Generate and display attendance reports with filtering and export
 */

class ReportsComponent {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        console.log('Initializing Reports component...');
        this.isInitialized = true;
    }

    async render() {
        console.log('Rendering Reports...');
        
        const container = document.getElementById('reportsView');
        if (!container) return;
        
        container.innerHTML = `
            <div class="reports-container">
                <h2>Reports & Analytics</h2>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h4>Generate Report</h4>
                    </div>
                    <div class="card-body">
                        <form id="reportForm">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label>From Date</label>
                                        <input type="date" class="form-control" id="dateFrom" required>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label>To Date</label>
                                        <input type="date" class="form-control" id="dateTo" required>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label>Location</label>
                                        <select class="form-control" id="reportLocation">
                                            <option value="">All Locations</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label>Person Type</label>
                                        <select class="form-control" id="reportPersonType">
                                            <option value="">All Types</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex gap-2">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-chart-bar"></i> Generate Report
                                </button>
                                <button type="button" class="btn btn-outline-secondary" id="exportReport">
                                    <i class="fas fa-download"></i> Export CSV
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h4>Attendance Records</h4>
                            </div>
                            <div class="card-body">
                                <div id="reportResults">
                                    <div class="text-center text-muted py-4">
                                        <i class="fas fa-chart-bar fa-3x mb-3"></i>
                                        <p>Select date range and click "Generate Report" to view attendance data</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h4>Statistics</h4>
                            </div>
                            <div class="card-body">
                                <div id="reportStats">
                                    <div class="text-center text-muted">
                                        <p>No data available</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.loadFilters();
        this.setDefaultDates();
    }

    setupEventListeners() {
        const reportForm = document.getElementById('reportForm');
        if (reportForm) {
            reportForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.generateReport();
            });
        }

        const exportBtn = document.getElementById('exportReport');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportReport());
        }
    }

    loadFilters() {
        const state = appState.getState();
        
        // Load locations
        const locationSelect = document.getElementById('reportLocation');
        if (locationSelect) {
            locationSelect.innerHTML = '<option value="">All Locations</option>' +
                state.locations.map(loc => 
                    `<option value="${loc.code}">${loc.name}</option>`
                ).join('');
        }
        
        // Load person types
        const personTypeSelect = document.getElementById('reportPersonType');
        if (personTypeSelect) {
            personTypeSelect.innerHTML = '<option value="">All Types</option>' +
                state.personTypes.map(pt => 
                    `<option value="${pt.code}">${pt.name}</option>`
                ).join('');
        }
    }

    setDefaultDates() {
        const today = new Date();
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        const dateFrom = document.getElementById('dateFrom');
        const dateTo = document.getElementById('dateTo');
        
        if (dateFrom) dateFrom.value = weekAgo.toISOString().split('T')[0];
        if (dateTo) dateTo.value = today.toISOString().split('T')[0];
    }

    async generateReport() {
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;
        const locationCode = document.getElementById('reportLocation').value;
        const personTypeCode = document.getElementById('reportPersonType').value;
        
        const loadingId = modalManager.showLoading('Generating report...');
        
        try {
            const result = await window.app.api.generateReport(
                dateFrom, dateTo, locationCode || null, personTypeCode || null
            );
            
            if (result.success) {
                this.displayReport(result.data);
            } else {
                throw new Error(result.error || 'Failed to generate report');
            }
        } catch (error) {
            console.error('Failed to generate report:', error);
            Utils.showToast(`Failed to generate report: ${error.message}`, 'error');
        } finally {
            modalManager.hideLoading();
        }
    }

    displayReport(reportData) {
        const { records, statistics } = reportData;
        
        // Display records
        const resultsContainer = document.getElementById('reportResults');
        if (resultsContainer) {
            if (records.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-inbox fa-3x mb-3"></i>
                        <p>No attendance records found for the selected criteria</p>
                    </div>
                `;
            } else {
                const columns = [
                    { key: 'person_name', label: 'Person' },
                    { key: 'person_type', label: 'Type' },
                    { key: 'location_name', label: 'Location' },
                    { key: 'check_in', label: 'Check In', formatter: TableHelpers.formatters.datetime },
                    { key: 'check_out', label: 'Check Out', formatter: TableHelpers.formatters.datetime },
                    { key: 'worked_hours', label: 'Hours', formatter: TableHelpers.formatters.duration },
                    { 
                        key: 'state', 
                        label: 'Status',
                        formatter: (value) => {
                            const statusClass = Utils.getStatusColor(value);
                            return `<span class="badge" style="background-color: ${statusClass}">${value}</span>`;
                        }
                    }
                ];
                
                resultsContainer.innerHTML = TableHelpers.createTable(records, columns);
            }
        }
        
        // Display statistics
        const statsContainer = document.getElementById('reportStats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stats-list">
                    <div class="stat-item">
                        <strong>Total Records:</strong>
                        <span>${statistics.total_records}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Total Hours:</strong>
                        <span>${Utils.formatDuration(statistics.total_hours)}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Average Hours:</strong>
                        <span>${Utils.formatDuration(statistics.average_hours)}</span>
                    </div>
                    <div class="stat-item">
                        <strong>Date Range:</strong>
                        <span>${Utils.formatDate(statistics.date_from)} - ${Utils.formatDate(statistics.date_to)}</span>
                    </div>
                </div>
            `;
        }
        
        // Store data for export
        this.currentReportData = records;
    }

    exportReport() {
        if (!this.currentReportData || this.currentReportData.length === 0) {
            Utils.showToast('No data to export', 'warning');
            return;
        }
        
        const headers = [
            'Person Name', 'Person Type', 'Location', 'Check In', 'Check Out', 
            'Worked Hours', 'Status'
        ];
        
        const csvData = this.currentReportData.map(record => ({
            'Person Name': record.person_name,
            'Person Type': record.person_type,
            'Location': record.location_name,
            'Check In': record.check_in,
            'Check Out': record.check_out || '',
            'Worked Hours': record.worked_hours,
            'Status': record.state
        }));
        
        const filename = `attendance_report_${new Date().toISOString().split('T')[0]}.csv`;
        Utils.exportAsCSV(csvData, filename, headers);
        
        Utils.showToast('Report exported successfully', 'success');
    }
}

window.ReportsComponent = ReportsComponent;
