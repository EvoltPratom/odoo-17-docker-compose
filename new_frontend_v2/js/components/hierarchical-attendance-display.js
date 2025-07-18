/**
 * Hierarchical Attendance Display Component
 * Shows current attendance with hierarchical location structure
 */

class HierarchicalAttendanceDisplay {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            showAutoActions: true,
            showTimestamps: true,
            showLocationPaths: true,
            groupByPerson: true,
            refreshInterval: 30000, // 30 seconds
            ...options
        };
        this.attendanceData = [];
        this.groupedData = {};
        this.refreshTimer = null;
    }

    /**
     * Initialize the component
     */
    async init() {
        await this.loadAttendanceData();
        this.render();
        this.startAutoRefresh();
    }

    /**
     * Load attendance data from API
     */
    async loadAttendanceData() {
        try {
            const result = await window.app.api.getCurrentAttendance();
            if (result && result.success) {
                this.attendanceData = result.data || [];
                this.groupedData = result.groupedData || {};
            }
        } catch (error) {
            console.error('Error loading attendance data:', error);
            this.attendanceData = [];
            this.groupedData = {};
        }
    }

    /**
     * Render the attendance display
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        const attendanceCount = this.attendanceData.length;
        const personCount = Object.keys(this.groupedData).length;

        container.innerHTML = `
            <div class="hierarchical-attendance-display">
                <div class="attendance-header">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">
                            <i class="fas fa-users me-2"></i>
                            Current Attendance
                        </h5>
                        <div class="attendance-stats">
                            <span class="badge bg-primary me-2">
                                ${personCount} ${personCount === 1 ? 'Person' : 'People'}
                            </span>
                            <span class="badge bg-info">
                                ${attendanceCount} ${attendanceCount === 1 ? 'Location' : 'Locations'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="attendance-controls mb-3">
                        <button class="btn btn-sm btn-outline-primary me-2" onclick="this.refresh()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-sm btn-outline-secondary me-2" onclick="this.toggleGrouping()">
                            <i class="fas fa-layer-group"></i> 
                            ${this.options.groupByPerson ? 'Show Flat' : 'Group by Person'}
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="this.toggleAutoActions()">
                            <i class="fas fa-robot"></i> 
                            ${this.options.showAutoActions ? 'Hide Auto' : 'Show Auto'}
                        </button>
                    </div>
                </div>
                
                <div class="attendance-content">
                    ${this.renderAttendanceContent()}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render attendance content based on grouping option
     */
    renderAttendanceContent() {
        if (this.attendanceData.length === 0) {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-user-clock fa-3x text-muted mb-3"></i>
                    <h6 class="text-muted">No one is currently checked in</h6>
                    <p class="text-muted small">Attendance records will appear here when people check in</p>
                </div>
            `;
        }

        if (this.options.groupByPerson) {
            return this.renderGroupedAttendance();
        } else {
            return this.renderFlatAttendance();
        }
    }

    /**
     * Render attendance grouped by person
     */
    renderGroupedAttendance() {
        const persons = Object.values(this.groupedData);
        
        return `
            <div class="grouped-attendance">
                ${persons.map(person => this.renderPersonAttendance(person)).join('')}
            </div>
        `;
    }

    /**
     * Render attendance for a single person
     */
    renderPersonAttendance(person) {
        const manualLocations = person.locations.filter(loc => loc.is_manual);
        const autoLocations = person.locations.filter(loc => loc.is_auto);
        
        return `
            <div class="person-attendance-card card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-user me-2"></i>
                            ${person.person_name}
                        </h6>
                        <span class="badge bg-success">
                            ${person.locations.length} ${person.locations.length === 1 ? 'Location' : 'Locations'}
                        </span>
                    </div>
                </div>
                <div class="card-body">
                    ${manualLocations.length > 0 ? `
                        <div class="manual-locations mb-3">
                            <h6 class="text-primary mb-2">
                                <i class="fas fa-hand-pointer me-1"></i>
                                Current Location${manualLocations.length > 1 ? 's' : ''}
                            </h6>
                            ${manualLocations.map(loc => this.renderLocationItem(loc, 'primary')).join('')}
                        </div>
                    ` : ''}
                    
                    ${this.options.showAutoActions && autoLocations.length > 0 ? `
                        <div class="auto-locations">
                            <h6 class="text-secondary mb-2">
                                <i class="fas fa-robot me-1"></i>
                                Auto Check-ins
                            </h6>
                            ${autoLocations.map(loc => this.renderLocationItem(loc, 'secondary')).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render a single location item
     */
    renderLocationItem(location, variant = 'primary') {
        const checkInTime = new Date(location.check_in).toLocaleTimeString();
        
        return `
            <div class="location-item d-flex justify-content-between align-items-center p-2 mb-2 border rounded">
                <div class="location-info">
                    <div class="location-name">
                        <i class="fas fa-map-marker-alt me-2 text-${variant}"></i>
                        <strong>${location.location_name}</strong>
                        ${location.is_auto ? '<i class="fas fa-robot ms-1 text-muted" title="Auto check-in"></i>' : ''}
                    </div>
                    ${this.options.showTimestamps ? `
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            Checked in at ${checkInTime}
                        </small>
                    ` : ''}
                    ${location.notes ? `
                        <small class="text-info d-block">
                            <i class="fas fa-info-circle me-1"></i>
                            ${location.notes}
                        </small>
                    ` : ''}
                </div>
                <div class="location-actions">
                    <span class="badge bg-${variant}">
                        ${location.is_manual ? 'Manual' : 'Auto'}
                    </span>
                </div>
            </div>
        `;
    }

    /**
     * Render flat attendance list
     */
    renderFlatAttendance() {
        return `
            <div class="flat-attendance">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Person</th>
                                <th>Location</th>
                                <th>Check-in Time</th>
                                <th>Type</th>
                                ${this.options.showAutoActions ? '<th>Notes</th>' : ''}
                            </tr>
                        </thead>
                        <tbody>
                            ${this.attendanceData.map(record => this.renderFlatAttendanceRow(record)).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    /**
     * Render a single flat attendance row
     */
    renderFlatAttendanceRow(record) {
        const checkInTime = new Date(record.check_in).toLocaleString();
        const isManual = record.auto_action === 'manual';
        
        return `
            <tr class="${isManual ? 'table-primary' : 'table-light'}">
                <td>
                    <i class="fas fa-user me-2"></i>
                    ${record.person_name}
                </td>
                <td>
                    <i class="fas fa-map-marker-alt me-2"></i>
                    ${record.location_name}
                </td>
                <td>
                    <i class="fas fa-clock me-2"></i>
                    ${checkInTime}
                </td>
                <td>
                    <span class="badge bg-${isManual ? 'primary' : 'secondary'}">
                        ${isManual ? 'Manual' : 'Auto'}
                        ${isManual ? '' : '<i class="fas fa-robot ms-1"></i>'}
                    </span>
                </td>
                ${this.options.showAutoActions ? `
                    <td>
                        <small class="text-muted">${record.notes || '-'}</small>
                    </td>
                ` : ''}
            </tr>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const container = document.getElementById(this.containerId);
        
        // Refresh button
        const refreshBtn = container.querySelector('[onclick="this.refresh()"]');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refresh();
        }

        // Toggle grouping button
        const groupBtn = container.querySelector('[onclick="this.toggleGrouping()"]');
        if (groupBtn) {
            groupBtn.onclick = () => this.toggleGrouping();
        }

        // Toggle auto actions button
        const autoBtn = container.querySelector('[onclick="this.toggleAutoActions()"]');
        if (autoBtn) {
            autoBtn.onclick = () => this.toggleAutoActions();
        }
    }

    /**
     * Refresh attendance data
     */
    async refresh() {
        await this.loadAttendanceData();
        this.render();
    }

    /**
     * Toggle grouping by person
     */
    toggleGrouping() {
        this.options.groupByPerson = !this.options.groupByPerson;
        this.render();
    }

    /**
     * Toggle showing auto actions
     */
    toggleAutoActions() {
        this.options.showAutoActions = !this.options.showAutoActions;
        this.render();
    }

    /**
     * Start auto refresh
     */
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        if (this.options.refreshInterval > 0) {
            this.refreshTimer = setInterval(() => {
                this.refresh();
            }, this.options.refreshInterval);
        }
    }

    /**
     * Stop auto refresh
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Destroy the component
     */
    destroy() {
        this.stopAutoRefresh();
    }
}

// Export for use in other modules
window.HierarchicalAttendanceDisplay = HierarchicalAttendanceDisplay;
