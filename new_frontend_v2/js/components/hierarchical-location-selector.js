/**
 * Hierarchical Location Selector Component
 * Displays locations in a tree structure with proper hierarchy
 */

class HierarchicalLocationSelector {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            allowMultiple: false,
            showPath: true,
            showCodes: true,
            onSelectionChange: null,
            ...options
        };
        this.locations = [];
        this.selectedLocations = new Set();
        this.hierarchy = null;
    }

    /**
     * Initialize the component with location data
     */
    async init(locations) {
        this.locations = locations || [];
        this.hierarchy = window.app.api.buildLocationHierarchy(this.locations);
        this.render();
    }

    /**
     * Render the hierarchical location selector
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        container.innerHTML = `
            <div class="hierarchical-location-selector">
                <div class="location-search">
                    <input type="text" 
                           id="${this.containerId}-search" 
                           placeholder="Search locations..." 
                           class="form-control mb-3">
                </div>
                <div class="location-tree" id="${this.containerId}-tree">
                    ${this.renderLocationTree()}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render the location tree structure
     */
    renderLocationTree() {
        if (!this.hierarchy || !this.hierarchy.rootLocations) {
            return '<div class="text-muted">No locations available</div>';
        }

        return `
            <div class="location-tree-container">
                ${this.hierarchy.rootLocations.map(location => this.renderLocationNode(location, 0)).join('')}
            </div>
        `;
    }

    /**
     * Render a single location node with its children
     */
    renderLocationNode(location, level) {
        const indent = level * 20;
        const hasChildren = location.children && location.children.length > 0;
        const isSelected = this.selectedLocations.has(location.id);
        
        const locationPath = this.options.showPath ? location.location_path : location.name;
        const locationCode = this.options.showCodes ? ` (${location.code})` : '';
        
        return `
            <div class="location-node" data-location-id="${location.id}" data-level="${level}">
                <div class="location-item ${isSelected ? 'selected' : ''}" 
                     style="padding-left: ${indent}px;">
                    ${hasChildren ? `
                        <span class="location-toggle" data-location-id="${location.id}">
                            <i class="fas fa-chevron-right"></i>
                        </span>
                    ` : '<span class="location-spacer"></span>'}
                    
                    <span class="location-icon">
                        <i class="fas ${this.getLocationIcon(location, level)}"></i>
                    </span>
                    
                    <span class="location-label" data-location-id="${location.id}">
                        ${location.name}${locationCode}
                    </span>
                    
                    ${this.options.showPath && location.location_path !== location.name ? `
                        <small class="text-muted ms-2">${location.location_path}</small>
                    ` : ''}
                    
                    <span class="location-info ms-auto">
                        ${location.capacity > 0 ? `
                            <small class="badge bg-secondary">
                                ${location.current_occupancy}/${location.capacity}
                            </small>
                        ` : ''}
                    </span>
                </div>
                
                ${hasChildren ? `
                    <div class="location-children" data-parent-id="${location.id}" style="display: none;">
                        ${location.children.map(child => this.renderLocationNode(child, level + 1)).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get appropriate icon for location based on level and type
     */
    getLocationIcon(location, level) {
        const code = location.code.toLowerCase();
        
        // Specific location type icons
        if (code.includes('building')) return 'fa-building';
        if (code.includes('room') || code.includes('classroom')) return 'fa-door-open';
        if (code.includes('lab')) return 'fa-flask';
        if (code.includes('library')) return 'fa-book';
        if (code.includes('office')) return 'fa-briefcase';
        if (code.includes('entrance')) return 'fa-sign-in-alt';
        if (code.includes('reception')) return 'fa-concierge-bell';
        if (code.includes('hall')) return 'fa-users';
        
        // Level-based icons
        switch (level) {
            case 0: return 'fa-building';
            case 1: return 'fa-layer-group';
            case 2: return 'fa-th-large';
            default: return 'fa-map-marker-alt';
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const container = document.getElementById(this.containerId);
        
        // Search functionality
        const searchInput = document.getElementById(`${this.containerId}-search`);
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterLocations(e.target.value);
            });
        }

        // Toggle expand/collapse
        container.addEventListener('click', (e) => {
            if (e.target.closest('.location-toggle')) {
                const locationId = e.target.closest('.location-toggle').dataset.locationId;
                this.toggleLocationNode(locationId);
            }
        });

        // Location selection
        container.addEventListener('click', (e) => {
            if (e.target.closest('.location-label')) {
                const locationId = parseInt(e.target.closest('.location-label').dataset.locationId);
                this.selectLocation(locationId);
            }
        });
    }

    /**
     * Toggle expand/collapse of location node
     */
    toggleLocationNode(locationId) {
        const childrenContainer = document.querySelector(`[data-parent-id="${locationId}"]`);
        const toggleIcon = document.querySelector(`[data-location-id="${locationId}"] .fa-chevron-right, [data-location-id="${locationId}"] .fa-chevron-down`);
        
        if (childrenContainer && toggleIcon) {
            const isExpanded = childrenContainer.style.display !== 'none';
            childrenContainer.style.display = isExpanded ? 'none' : 'block';
            toggleIcon.className = isExpanded ? 'fas fa-chevron-right' : 'fas fa-chevron-down';
        }
    }

    /**
     * Select/deselect a location
     */
    selectLocation(locationId) {
        if (!this.options.allowMultiple) {
            this.selectedLocations.clear();
        }

        if (this.selectedLocations.has(locationId)) {
            this.selectedLocations.delete(locationId);
        } else {
            this.selectedLocations.add(locationId);
        }

        this.updateSelectionDisplay();
        
        if (this.options.onSelectionChange) {
            const selectedLocationData = this.getSelectedLocationData();
            this.options.onSelectionChange(selectedLocationData);
        }
    }

    /**
     * Update visual selection display
     */
    updateSelectionDisplay() {
        const container = document.getElementById(this.containerId);
        container.querySelectorAll('.location-item').forEach(item => {
            const locationId = parseInt(item.querySelector('.location-label').dataset.locationId);
            item.classList.toggle('selected', this.selectedLocations.has(locationId));
        });
    }

    /**
     * Filter locations based on search term
     */
    filterLocations(searchTerm) {
        const container = document.getElementById(`${this.containerId}-tree`);
        const nodes = container.querySelectorAll('.location-node');
        
        if (!searchTerm.trim()) {
            // Show all nodes
            nodes.forEach(node => {
                node.style.display = 'block';
            });
            return;
        }

        const term = searchTerm.toLowerCase();
        nodes.forEach(node => {
            const locationId = parseInt(node.dataset.locationId);
            const location = this.hierarchy.locationMap[locationId];
            
            const matches = location.name.toLowerCase().includes(term) ||
                          location.code.toLowerCase().includes(term) ||
                          (location.location_path && location.location_path.toLowerCase().includes(term));
            
            node.style.display = matches ? 'block' : 'none';
        });
    }

    /**
     * Get selected location data
     */
    getSelectedLocationData() {
        return Array.from(this.selectedLocations).map(id => {
            return this.hierarchy.locationMap[id];
        });
    }

    /**
     * Set selected locations programmatically
     */
    setSelectedLocations(locationIds) {
        this.selectedLocations = new Set(locationIds);
        this.updateSelectionDisplay();
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        this.selectedLocations.clear();
        this.updateSelectionDisplay();
    }

    /**
     * Expand all location nodes
     */
    expandAll() {
        const container = document.getElementById(this.containerId);
        container.querySelectorAll('.location-children').forEach(children => {
            children.style.display = 'block';
        });
        container.querySelectorAll('.fa-chevron-right').forEach(icon => {
            icon.className = 'fas fa-chevron-down';
        });
    }

    /**
     * Collapse all location nodes
     */
    collapseAll() {
        const container = document.getElementById(this.containerId);
        container.querySelectorAll('.location-children').forEach(children => {
            children.style.display = 'none';
        });
        container.querySelectorAll('.fa-chevron-down').forEach(icon => {
            icon.className = 'fas fa-chevron-right';
        });
    }
}

// Export for use in other modules
window.HierarchicalLocationSelector = HierarchicalLocationSelector;
