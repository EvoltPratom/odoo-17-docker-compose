/**
 * Dashboard Component
 * Real-time overview of attendance system with stats and current attendance
 */

class DashboardComponent {
    constructor() {
        this.refreshInterval = null;
        this.isInitialized = false;
        this.hierarchicalAttendanceDisplay = null;
    }

    /**
     * Initialize the dashboard component
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('Initializing Dashboard component...');
        
        // Subscribe to state changes
        appState.subscribe('stats', () => {
            this.updateStats();
        });
        
        appState.subscribe('currentAttendance', () => {
            this.updateCurrentAttendance();
        });
        
        // Set up event listeners
        this.setupEventListeners();
        
        this.isInitialized = true;
        console.log('Dashboard component initialized');
    }

    /**
     * Render the dashboard
     */
    async render() {
        console.log('Rendering Dashboard...');
        
        try {
            // Update stats
            this.updateStats();
            
            // Update current attendance
            this.updateCurrentAttendance();
            
            // Start auto-refresh
            this.startAutoRefresh();
            
        } catch (error) {
            console.error('Failed to render dashboard:', error);
            Utils.showToast('Failed to load dashboard', 'error');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Refresh current attendance button
        const refreshBtn = document.getElementById('refreshCurrentAttendance');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                await this.refreshCurrentAttendance();
            });
        }

        // Quick action buttons (will be added dynamically)
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-quick-action]')) {
                const action = e.target.closest('[data-quick-action]').dataset.quickAction;
                this.handleQuickAction(action);
            }
        });
    }

    /**
     * Update dashboard statistics
     */
    updateStats() {
        const state = appState.getState();
        const stats = state.stats;
        
        // Update stat values
        this.updateStatValue('totalPersons', stats.totalPersons);
        this.updateStatValue('currentlyCheckedIn', stats.currentlyCheckedIn);
        this.updateStatValue('totalLocations', stats.totalLocations);
        this.updateStatValue('todayAttendance', stats.todayAttendance);
        
        console.log('Dashboard stats updated:', stats);
    }

    /**
     * Update a single stat value
     */
    updateStatValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            // Animate the number change
            this.animateNumber(element, parseInt(element.textContent) || 0, value);
        }
    }

    /**
     * Animate number changes
     */
    animateNumber(element, from, to) {
        const duration = 1000;
        const steps = 20;
        const stepValue = (to - from) / steps;
        const stepDuration = duration / steps;
        
        let current = from;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            current += stepValue;
            
            if (step >= steps) {
                current = to;
                clearInterval(timer);
            }
            
            element.textContent = Math.round(current);
        }, stepDuration);
    }

    /**
     * Update current attendance list
     */
    updateCurrentAttendance() {
        const state = appState.getState();
        const currentAttendance = state.currentAttendance;
        const container = document.getElementById('currentAttendanceList');

        if (!container) return;

        // Initialize hierarchical attendance display if not already done
        if (!this.hierarchicalAttendanceDisplay) {
            // Create a container for the hierarchical display
            container.innerHTML = '<div id="hierarchicalAttendanceContainer"></div>';

            this.hierarchicalAttendanceDisplay = new HierarchicalAttendanceDisplay(
                'hierarchicalAttendanceContainer',
                {
                    showAutoActions: true,
                    showTimestamps: true,
                    showLocationPaths: true,
                    groupByPerson: true,
                    refreshInterval: 0 // We'll handle refresh manually
                }
            );
        }

        // Update the hierarchical display with current data
        this.hierarchicalAttendanceDisplay.attendanceData = currentAttendance;
        this.hierarchicalAttendanceDisplay.groupedData = window.app.api.groupAttendanceByPerson(currentAttendance);
        this.hierarchicalAttendanceDisplay.render();
    }

    /**
     * Create person card for current attendance
     */
    createPersonCard(person) {
        const checkInTime = Utils.formatDate(person.check_in, 'HH:mm');
        const duration = person.duration_display || 'Unknown';
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card">
                    <div class="card-body p-3">
                        <div class="d-flex align-items-center">
                            <div class="person-avatar me-3" style="width: 40px; height: 40px; font-size: 1rem;">
                                ${person.person_name.charAt(0).toUpperCase()}
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${Utils.sanitizeHtml(person.person_name)}</h6>
                                <small class="text-muted">
                                    <i class="fas fa-clock"></i> ${checkInTime} (${duration})
                                </small>
                            </div>
                            <button class="btn btn-sm btn-outline-danger" 
                                    data-quick-action="check-out" 
                                    data-person-name="${person.person_name}"
                                    title="Check Out">
                                <i class="fas fa-sign-out-alt"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Handle quick actions
     */
    async handleQuickAction(action, data = {}) {
        try {
            switch (action) {
                case 'check-in':
                    await this.showCheckInModal();
                    break;
                    
                case 'check-out':
                    await this.handleQuickCheckOut(data);
                    break;
                    
                case 'add-person':
                    // Navigate to persons view
                    appState.setCurrentView('persons');
                    break;
                    
                case 'add-location':
                    // Navigate to locations view
                    appState.setCurrentView('locations');
                    break;
                    
                default:
                    console.warn('Unknown quick action:', action);
            }
        } catch (error) {
            console.error('Quick action failed:', error);
            Utils.showToast(`Action failed: ${error.message}`, 'error');
        }
    }

    /**
     * Show check-in modal
     */
    async showCheckInModal() {
        const state = appState.getState();
        const persons = state.persons;
        const locations = state.locations;

        if (persons.length === 0) {
            Utils.showToast('No persons available. Please add persons first.', 'warning');
            return;
        }

        if (locations.length === 0) {
            Utils.showToast('No locations available. Please add locations first.', 'warning');
            return;
        }

        // Show custom modal with hierarchical location selector
        const modal = modalManager.showModal({
            title: 'Quick Check-In',
            content: `
                <div class="check-in-form">
                    <div class="form-group mb-3">
                        <label for="personSelect" class="form-label">Select Person</label>
                        <select id="personSelect" class="form-select" required>
                            <option value="">Choose a person...</option>
                            ${persons.map(p => `
                                <option value="${p.person_id}">${p.name} (${p.person_id})</option>
                            `).join('')}
                        </select>
                    </div>

                    <div class="form-group mb-3">
                        <label class="form-label">Select Location</label>
                        <div id="hierarchicalLocationSelector" style="max-height: 300px; overflow-y: auto;"></div>
                    </div>
                </div>
            `,
            buttons: [
                {
                    text: 'Cancel',
                    variant: 'secondary',
                    action: () => modalManager.hideModal()
                },
                {
                    text: 'Check In',
                    variant: 'primary',
                    action: async () => {
                        const personId = document.getElementById('personSelect').value;
                        const locationSelector = this.hierarchicalLocationSelector;
                        const selectedLocations = locationSelector ? locationSelector.getSelectedLocationData() : [];

                        if (!personId) {
                            Utils.showToast('Please select a person', 'warning');
                            return;
                        }

                        if (selectedLocations.length === 0) {
                            Utils.showToast('Please select a location', 'warning');
                            return;
                        }

                        modalManager.hideModal();
                        await this.performCheckIn(personId, selectedLocations[0].code);
                    }
                }
            ]
        });

        // Initialize hierarchical location selector
        setTimeout(() => {
            this.hierarchicalLocationSelector = new HierarchicalLocationSelector(
                'hierarchicalLocationSelector',
                {
                    allowMultiple: false,
                    showPath: true,
                    showCodes: true,
                    onSelectionChange: (selectedLocations) => {
                        // Update UI to show selection
                        console.log('Selected locations:', selectedLocations);
                    }
                }
            );
            this.hierarchicalLocationSelector.init(locations);
        }, 100);
    }

    /**
     * Handle quick check-out
     */
    async handleQuickCheckOut(data) {
        const personName = data.personName || 'this person';
        
        const confirmed = await modalManager.confirm({
            title: 'Check Out',
            message: `Check out ${personName}?`,
            confirmText: 'Check Out'
        });
        
        if (confirmed) {
            // Find the person identifier from current attendance
            const state = appState.getState();
            const attendance = state.currentAttendance.find(a => a.person_name === personName);
            
            if (attendance) {
                await this.performCheckOut(attendance.person_id || personName);
            }
        }
    }

    /**
     * Perform check-in
     */
    async performCheckIn(personIdentifier, locationCode) {
        const loadingId = modalManager.showLoading('Checking in...');
        
        try {
            const result = await window.app.api.checkIn(personIdentifier, locationCode);
            
            if (result.success) {
                Utils.showToast(result.message || 'Check-in successful', 'success');
                await this.refreshCurrentAttendance();
            } else {
                throw new Error(result.error || 'Check-in failed');
            }
        } catch (error) {
            console.error('Check-in failed:', error);
            Utils.showToast(`Check-in failed: ${error.message}`, 'error');
        } finally {
            modalManager.hideLoading();
        }
    }

    /**
     * Perform check-out
     */
    async performCheckOut(personIdentifier) {
        const loadingId = modalManager.showLoading('Checking out...');
        
        try {
            const result = await window.app.api.checkOut(personIdentifier);
            
            if (result.success) {
                Utils.showToast(result.message || 'Check-out successful', 'success');
                await this.refreshCurrentAttendance();
            } else {
                throw new Error(result.error || 'Check-out failed');
            }
        } catch (error) {
            console.error('Check-out failed:', error);
            Utils.showToast(`Check-out failed: ${error.message}`, 'error');
        } finally {
            modalManager.hideLoading();
        }
    }

    /**
     * Refresh current attendance
     */
    async refreshCurrentAttendance() {
        try {
            const result = await window.app.api.getCurrentAttendance();
            
            if (result.success) {
                appState.setState({
                    currentAttendance: result.data || []
                });
                
                // Update statistics
                appState.updateStatistics();
            }
        } catch (error) {
            console.error('Failed to refresh current attendance:', error);
            Utils.showToast('Failed to refresh attendance', 'error');
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        // Clear existing interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Set up new interval (every 30 seconds)
        this.refreshInterval = setInterval(async () => {
            if (appState.getState().ui.currentView === 'dashboard') {
                await this.refreshCurrentAttendance();
            }
        }, Constants.DEFAULTS.REFRESH_INTERVAL);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Cleanup when component is destroyed
     */
    destroy() {
        this.stopAutoRefresh();
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.DashboardComponent = DashboardComponent;
