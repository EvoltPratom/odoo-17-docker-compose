/**
 * Locations Component
 * Manage attendance locations with CRUD operations and occupancy tracking
 */

class LocationsComponent {
    constructor() {
        this.isInitialized = false;
        this.currentView = 'grid'; // grid or list
        this.searchTerm = '';
        this.selectedLocation = null;
    }

    /**
     * Initialize the locations component
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('Initializing Locations component...');
        
        // Subscribe to state changes
        appState.subscribe('locations', () => {
            this.renderLocationsList();
        });
        
        this.isInitialized = true;
        console.log('Locations component initialized');
    }

    /**
     * Render the locations view
     */
    async render() {
        console.log('Rendering Locations...');
        
        const container = document.getElementById('locationsView');
        if (!container) return;
        
        container.innerHTML = this.getLocationsHTML();
        this.setupEventListeners();
        this.renderLocationsList();
    }

    /**
     * Get the main locations HTML structure
     */
    getLocationsHTML() {
        return `
            <div class="locations-container">
                <!-- Header with actions -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Locations Management</h2>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-secondary" id="toggleView">
                            <i class="fas fa-th" id="viewIcon"></i>
                        </button>
                        <button class="btn btn-primary" id="addLocationBtn">
                            <i class="fas fa-plus"></i> Add Location
                        </button>
                    </div>
                </div>

                <!-- Search and filters -->
                <div class="search-filters">
                    <div class="search-row">
                        <div class="form-group">
                            <input type="text" class="form-control" id="locationSearch" 
                                   placeholder="Search locations..." value="${this.searchTerm}">
                        </div>
                        <div class="filter-group">
                            <select class="form-control" id="buildingFilter">
                                <option value="">All Buildings</option>
                            </select>
                            <select class="form-control" id="statusFilter">
                                <option value="">All Status</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                            </select>
                        </div>
                        <button class="btn btn-outline-secondary" id="clearFilters">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                </div>

                <!-- Locations list/grid -->
                <div id="locationsList" class="locations-list">
                    <!-- Locations will be rendered here -->
                </div>
            </div>
        `;
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Add location button
        const addBtn = document.getElementById('addLocationBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showLocationModal());
        }

        // Toggle view button
        const toggleBtn = document.getElementById('toggleView');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleView());
        }

        // Search input
        const searchInput = document.getElementById('locationSearch');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce((e) => {
                this.searchTerm = e.target.value;
                this.renderLocationsList();
            }, 300));
        }

        // Filters
        const buildingFilter = document.getElementById('buildingFilter');
        const statusFilter = document.getElementById('statusFilter');
        
        if (buildingFilter) {
            buildingFilter.addEventListener('change', () => this.renderLocationsList());
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.renderLocationsList());
        }

        // Clear filters
        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }

        // Location actions (delegated)
        document.addEventListener('click', (e) => {
            const locationCard = e.target.closest('[data-location-id]');
            if (!locationCard) return;
            
            const locationId = parseInt(locationCard.dataset.locationId);
            
            if (e.target.closest('[data-action="edit"]')) {
                e.stopPropagation();
                this.editLocation(locationId);
            } else if (e.target.closest('[data-action="delete"]')) {
                e.stopPropagation();
                this.deleteLocation(locationId);
            } else if (e.target.closest('[data-action="view-occupants"]')) {
                e.stopPropagation();
                this.viewOccupants(locationId);
            } else {
                // Click on card itself - show details
                this.showLocationDetails(locationId);
            }
        });
    }

    /**
     * Render locations list
     */
    renderLocationsList() {
        const container = document.getElementById('locationsList');
        if (!container) return;
        
        const state = appState.getState();
        let locations = [...state.locations];
        
        // Apply search filter
        if (this.searchTerm) {
            locations = Utils.filterBySearch(locations, this.searchTerm, 
                ['name', 'code', 'building', 'description']);
        }
        
        // Apply building filter
        const buildingFilter = document.getElementById('buildingFilter');
        if (buildingFilter && buildingFilter.value) {
            locations = locations.filter(loc => loc.building === buildingFilter.value);
        }
        
        // Apply status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter && statusFilter.value) {
            const isActive = statusFilter.value === 'active';
            locations = locations.filter(loc => loc.active === isActive);
        }
        
        // Update building filter options
        this.updateBuildingFilter(state.locations);
        
        // Render based on current view
        if (this.currentView === 'grid') {
            container.className = 'location-grid';
            container.innerHTML = locations.map(loc => this.createLocationCard(loc)).join('');
        } else {
            container.className = 'locations-table-container';
            container.innerHTML = this.createLocationsTable(locations);
        }
        
        if (locations.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-map-marker-alt fa-3x mb-3"></i>
                    <h4>No locations found</h4>
                    <p>No locations match your current filters.</p>
                    <button class="btn btn-primary" id="addFirstLocation">
                        <i class="fas fa-plus"></i> Add First Location
                    </button>
                </div>
            `;
            
            // Add event listener for first location button
            const addFirstBtn = document.getElementById('addFirstLocation');
            if (addFirstBtn) {
                addFirstBtn.addEventListener('click', () => this.showLocationModal());
            }
        }
    }

    /**
     * Create location card for grid view
     */
    createLocationCard(location) {
        const occupancyPercentage = Utils.calculateOccupancy(location.current_occupancy, location.capacity);
        const occupancyStatus = Utils.getOccupancyStatus(occupancyPercentage);
        
        return `
            <div class="location-card" data-location-id="${location.id}">
                <div class="location-card-header">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="location-name">${Utils.sanitizeHtml(location.name)}</h5>
                            <div class="location-code">${Utils.sanitizeHtml(location.code)}</div>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <div class="dropdown-menu">
                                <a class="dropdown-item" href="#" data-action="edit">
                                    <i class="fas fa-edit"></i> Edit
                                </a>
                                <a class="dropdown-item" href="#" data-action="view-occupants">
                                    <i class="fas fa-users"></i> View Occupants
                                </a>
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item text-danger" href="#" data-action="delete">
                                    <i class="fas fa-trash"></i> Delete
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="location-card-body">
                    ${location.building ? `
                        <div class="mb-2">
                            <i class="fas fa-building text-muted"></i>
                            ${Utils.sanitizeHtml(location.building)}
                            ${location.floor ? ` - ${Utils.sanitizeHtml(location.floor)}` : ''}
                        </div>
                    ` : ''}
                    
                    <div class="occupancy-info">
                        <div class="occupancy-text">
                            <span>Occupancy</span>
                            <span>${location.current_occupancy || 0}${location.capacity ? ` / ${location.capacity}` : ''}</span>
                        </div>
                        ${location.capacity ? `
                            <div class="occupancy-bar">
                                <div class="occupancy-fill ${occupancyStatus}" 
                                     style="width: ${occupancyPercentage}%"></div>
                            </div>
                            <small class="text-muted">${occupancyPercentage}% occupied</small>
                        ` : ''}
                    </div>
                    
                    <div class="mt-3">
                        <span class="badge ${location.active ? 'badge-success' : 'badge-secondary'}">
                            ${location.active ? 'Active' : 'Inactive'}
                        </span>
                        ${location.requires_permission ? '<span class="badge badge-warning">Restricted</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create locations table for list view
     */
    createLocationsTable(locations) {
        const rows = locations.map(location => {
            const occupancyPercentage = Utils.calculateOccupancy(location.current_occupancy, location.capacity);
            
            return `
                <tr data-location-id="${location.id}">
                    <td>
                        <strong>${Utils.sanitizeHtml(location.name)}</strong><br>
                        <small class="text-muted">${Utils.sanitizeHtml(location.code)}</small>
                    </td>
                    <td>${Utils.sanitizeHtml(location.building || '-')}</td>
                    <td>${Utils.sanitizeHtml(location.floor || '-')}</td>
                    <td>
                        ${location.current_occupancy || 0}${location.capacity ? ` / ${location.capacity}` : ''}
                        ${location.capacity ? `<br><small class="text-muted">${occupancyPercentage}%</small>` : ''}
                    </td>
                    <td>
                        <span class="badge ${location.active ? 'badge-success' : 'badge-secondary'}">
                            ${location.active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" data-action="edit" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-info" data-action="view-occupants" title="View Occupants">
                                <i class="fas fa-users"></i>
                            </button>
                            <button class="btn btn-outline-danger" data-action="delete" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        
        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Building</th>
                        <th>Floor</th>
                        <th>Occupancy</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        `;
    }

    /**
     * Update building filter options
     */
    updateBuildingFilter(locations) {
        const buildingFilter = document.getElementById('buildingFilter');
        if (!buildingFilter) return;
        
        const buildings = [...new Set(locations.map(loc => loc.building).filter(Boolean))];
        const currentValue = buildingFilter.value;
        
        buildingFilter.innerHTML = '<option value="">All Buildings</option>' +
            buildings.map(building => 
                `<option value="${building}" ${building === currentValue ? 'selected' : ''}>${building}</option>`
            ).join('');
    }

    /**
     * Toggle between grid and list view
     */
    toggleView() {
        this.currentView = this.currentView === 'grid' ? 'list' : 'grid';
        
        const viewIcon = document.getElementById('viewIcon');
        if (viewIcon) {
            viewIcon.className = this.currentView === 'grid' ? 'fas fa-list' : 'fas fa-th';
        }
        
        this.renderLocationsList();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        this.searchTerm = '';
        
        const searchInput = document.getElementById('locationSearch');
        const buildingFilter = document.getElementById('buildingFilter');
        const statusFilter = document.getElementById('statusFilter');
        
        if (searchInput) searchInput.value = '';
        if (buildingFilter) buildingFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        
        this.renderLocationsList();
    }

    /**
     * Show location modal for create/edit
     */
    async showLocationModal(locationId = null) {
        const isEdit = locationId !== null;
        const state = appState.getState();
        const location = isEdit ? state.locations.find(l => l.id === locationId) : {};
        
        const formData = await modalManager.showForm({
            title: isEdit ? 'Edit Location' : 'Add New Location',
            fields: [
                {
                    name: 'name',
                    label: 'Location Name',
                    type: 'text',
                    required: true,
                    defaultValue: location.name || '',
                    placeholder: 'e.g., Main Entrance, Library, Classroom 101'
                },
                {
                    name: 'code',
                    label: 'Location Code',
                    type: 'text',
                    required: true,
                    defaultValue: location.code || '',
                    placeholder: 'e.g., MAIN_ENT, LIB, CLASS_101',
                    help: 'Unique identifier for the location (uppercase, no spaces)'
                },
                {
                    name: 'description',
                    label: 'Description',
                    type: 'textarea',
                    defaultValue: location.description || '',
                    placeholder: 'Optional description of the location'
                },
                {
                    name: 'building',
                    label: 'Building',
                    type: 'text',
                    defaultValue: location.building || '',
                    placeholder: 'e.g., Main Building, Academic Block'
                },
                {
                    name: 'floor',
                    label: 'Floor',
                    type: 'text',
                    defaultValue: location.floor || '',
                    placeholder: 'e.g., Ground Floor, 2nd Floor'
                },
                {
                    name: 'capacity',
                    label: 'Capacity',
                    type: 'number',
                    defaultValue: location.capacity || '',
                    placeholder: 'Maximum number of people (optional)'
                }
            ],
            submitText: isEdit ? 'Update Location' : 'Create Location',
            onSubmit: async (data) => {
                return await this.saveLocation(data, locationId);
            }
        });
    }

    /**
     * Save location (create or update)
     */
    async saveLocation(data, locationId = null) {
        const loadingId = modalManager.showLoading(locationId ? 'Updating location...' : 'Creating location...');
        
        try {
            let result;
            if (locationId) {
                result = await window.app.api.updateLocation(locationId, data);
            } else {
                result = await window.app.api.createLocation(data);
            }
            
            if (result.success) {
                Utils.showToast(
                    locationId ? 'Location updated successfully' : 'Location created successfully',
                    'success'
                );
                
                // Reload locations data
                await appState.loadData();
                return true;
            } else {
                throw new Error(result.error || 'Failed to save location');
            }
        } catch (error) {
            console.error('Failed to save location:', error);
            Utils.showToast(`Failed to save location: ${error.message}`, 'error');
            return false;
        } finally {
            modalManager.hideLoading();
        }
    }

    /**
     * Edit location
     */
    editLocation(locationId) {
        this.showLocationModal(locationId);
    }

    /**
     * Delete location
     */
    async deleteLocation(locationId) {
        const state = appState.getState();
        const location = state.locations.find(l => l.id === locationId);
        
        if (!location) return;
        
        const confirmed = await modalManager.confirm({
            title: 'Delete Location',
            message: `Are you sure you want to delete "${location.name}"? This action cannot be undone.`,
            confirmText: 'Delete',
            onConfirm: async () => {
                const loadingId = modalManager.showLoading('Deleting location...');
                
                try {
                    const result = await window.app.api.deleteLocation(locationId);
                    
                    if (result.success) {
                        Utils.showToast('Location deleted successfully', 'success');
                        await appState.loadData();
                    } else {
                        throw new Error(result.error || 'Failed to delete location');
                    }
                } catch (error) {
                    console.error('Failed to delete location:', error);
                    Utils.showToast(`Failed to delete location: ${error.message}`, 'error');
                } finally {
                    modalManager.hideLoading();
                }
            }
        });
    }

    /**
     * View occupants of a location
     */
    async viewOccupants(locationId) {
        const state = appState.getState();
        const location = state.locations.find(l => l.id === locationId);
        const currentAttendance = state.currentAttendance.filter(a => a.location_id === locationId);
        
        if (!location) return;
        
        let bodyHtml = '';
        
        if (currentAttendance.length === 0) {
            bodyHtml = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-users fa-2x mb-3"></i>
                    <p>No one is currently at this location</p>
                </div>
            `;
        } else {
            bodyHtml = `
                <div class="occupants-list">
                    ${currentAttendance.map(person => `
                        <div class="d-flex align-items-center justify-content-between p-3 border-bottom">
                            <div>
                                <strong>${Utils.sanitizeHtml(person.person_name)}</strong><br>
                                <small class="text-muted">
                                    Checked in at ${Utils.formatDate(person.check_in, 'HH:mm')}
                                    (${person.duration_display})
                                </small>
                            </div>
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="app.components.dashboard.performCheckOut('${person.person_id}')">
                                <i class="fas fa-sign-out-alt"></i> Check Out
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        modalManager.show({
            title: `Current Occupants - ${location.name}`,
            body: bodyHtml,
            size: 'md'
        });
    }

    /**
     * Show location details
     */
    showLocationDetails(locationId) {
        const state = appState.getState();
        const location = state.locations.find(l => l.id === locationId);
        
        if (!location) return;
        
        const occupancyPercentage = Utils.calculateOccupancy(location.current_occupancy, location.capacity);
        
        const bodyHtml = `
            <div class="location-details">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Basic Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Name:</strong></td><td>${Utils.sanitizeHtml(location.name)}</td></tr>
                            <tr><td><strong>Code:</strong></td><td>${Utils.sanitizeHtml(location.code)}</td></tr>
                            <tr><td><strong>Building:</strong></td><td>${Utils.sanitizeHtml(location.building || '-')}</td></tr>
                            <tr><td><strong>Floor:</strong></td><td>${Utils.sanitizeHtml(location.floor || '-')}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Occupancy</h6>
                        <div class="occupancy-info">
                            <div class="occupancy-text">
                                <span>Current:</span>
                                <span>${location.current_occupancy || 0}${location.capacity ? ` / ${location.capacity}` : ''}</span>
                            </div>
                            ${location.capacity ? `
                                <div class="occupancy-bar mt-2">
                                    <div class="occupancy-fill" style="width: ${occupancyPercentage}%"></div>
                                </div>
                                <small class="text-muted">${occupancyPercentage}% occupied</small>
                            ` : ''}
                        </div>
                    </div>
                </div>
                
                ${location.description ? `
                    <div class="mt-3">
                        <h6>Description</h6>
                        <p>${Utils.sanitizeHtml(location.description)}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        modalManager.show({
            title: `Location Details - ${location.name}`,
            body: bodyHtml,
            size: 'lg',
            buttons: [
                {
                    id: 'edit',
                    text: 'Edit Location',
                    className: 'btn btn-primary',
                    onClick: () => {
                        this.editLocation(locationId);
                        return false; // Keep modal open
                    }
                }
            ]
        });
    }
}

// Export for use in other modules
window.LocationsComponent = LocationsComponent;
