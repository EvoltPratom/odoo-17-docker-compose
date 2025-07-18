/**
 * Attendance Component
 * Handle check-in/check-out operations and attendance tracking
 */

class AttendanceComponent {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        console.log('Initializing Attendance component...');
        this.isInitialized = true;
    }

    async render() {
        console.log('Rendering Attendance...');
        
        const container = document.getElementById('attendanceView');
        if (!container) return;
        
        container.innerHTML = `
            <div class="attendance-container">
                <h2>Attendance Management</h2>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4>Quick Check-In</h4>
                            </div>
                            <div class="card-body">
                                <form id="checkInForm">
                                    <div class="form-group">
                                        <label>Person ID / Barcode</label>
                                        <input type="text" class="form-control" id="personIdentifier" required>
                                    </div>
                                    <div class="form-group">
                                        <label>Location</label>
                                        <select class="form-control" id="locationSelect" required>
                                            <option value="">Select Location</option>
                                        </select>
                                    </div>
                                    <button type="submit" class="btn btn-success">
                                        <i class="fas fa-sign-in-alt"></i> Check In
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4>Quick Check-Out</h4>
                            </div>
                            <div class="card-body">
                                <form id="checkOutForm">
                                    <div class="form-group">
                                        <label>Person ID / Barcode</label>
                                        <input type="text" class="form-control" id="personIdentifierOut" required>
                                    </div>
                                    <button type="submit" class="btn btn-warning">
                                        <i class="fas fa-sign-out-alt"></i> Check Out
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h4>Current Attendance</h4>
                    </div>
                    <div class="card-body">
                        <div id="currentAttendanceTable">
                            <!-- Current attendance will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.loadLocations();
        this.loadCurrentAttendance();
    }

    setupEventListeners() {
        // Check-in form
        const checkInForm = document.getElementById('checkInForm');
        if (checkInForm) {
            checkInForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleCheckIn();
            });
        }

        // Check-out form
        const checkOutForm = document.getElementById('checkOutForm');
        if (checkOutForm) {
            checkOutForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleCheckOut();
            });
        }
    }

    async loadLocations() {
        const state = appState.getState();
        const locationSelect = document.getElementById('locationSelect');
        
        if (locationSelect) {
            locationSelect.innerHTML = '<option value="">Select Location</option>' +
                state.locations.map(loc => 
                    `<option value="${loc.code}">${loc.name} (${loc.code})</option>`
                ).join('');
        }
    }

    async loadCurrentAttendance() {
        const state = appState.getState();
        const container = document.getElementById('currentAttendanceTable');
        
        if (!container) return;
        
        const columns = [
            { key: 'person_name', label: 'Person' },
            { key: 'location_name', label: 'Location' },
            { key: 'check_in', label: 'Check In', formatter: TableHelpers.formatters.datetime },
            { key: 'duration_display', label: 'Duration' }
        ];
        
        container.innerHTML = TableHelpers.createTable(state.currentAttendance, columns);
    }

    async handleCheckIn() {
        const personIdentifier = document.getElementById('personIdentifier').value;
        const locationCode = document.getElementById('locationSelect').value;
        
        try {
            const result = await window.app.api.checkIn(personIdentifier, locationCode);
            
            if (result.success) {
                Utils.showToast('Check-in successful', 'success');
                document.getElementById('checkInForm').reset();
                await appState.loadData();
                this.loadCurrentAttendance();
            } else {
                throw new Error(result.error || 'Check-in failed');
            }
        } catch (error) {
            Utils.showToast(`Check-in failed: ${error.message}`, 'error');
        }
    }

    async handleCheckOut() {
        const personIdentifier = document.getElementById('personIdentifierOut').value;
        
        try {
            const result = await window.app.api.checkOut(personIdentifier);
            
            if (result.success) {
                Utils.showToast('Check-out successful', 'success');
                document.getElementById('checkOutForm').reset();
                await appState.loadData();
                this.loadCurrentAttendance();
            } else {
                throw new Error(result.error || 'Check-out failed');
            }
        } catch (error) {
            Utils.showToast(`Check-out failed: ${error.message}`, 'error');
        }
    }
}

window.AttendanceComponent = AttendanceComponent;
