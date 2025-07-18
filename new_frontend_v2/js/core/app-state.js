/**
 * Application State Management
 * Centralized state management for the Extended Attendance System
 */

class AppState {
    constructor() {
        this.state = {
            // User and authentication
            user: {
                uid: null,
                username: '',
                role: 'user', // user, officer, manager
                permissions: [],
                isAuthenticated: false
            },

            // Connection status
            connection: {
                isConnected: false,
                url: '',
                database: '',
                useMockData: false
            },

            // Core data
            personTypes: [],
            locations: [],
            persons: [],
            currentAttendance: [],
            attendanceRecords: [],

            // UI state
            ui: {
                currentView: 'dashboard',
                selectedLocation: null,
                selectedPerson: null,
                selectedPersonType: null,
                sidebarCollapsed: false,
                theme: 'light'
            },

            // Filters and search
            filters: {
                dateRange: {
                    from: new Date().toISOString().split('T')[0],
                    to: new Date().toISOString().split('T')[0]
                },
                personType: null,
                location: null,
                searchTerm: ''
            },

            // Statistics and analytics
            stats: {
                totalPersons: 0,
                totalLocations: 0,
                currentlyCheckedIn: 0,
                todayAttendance: 0,
                locationOccupancy: {}
            }
        };

        this.listeners = {};
        this.api = null;
    }

    /**
     * Initialize the state management system
     */
    init(apiInstance) {
        this.api = apiInstance;
        this.loadFromLocalStorage();
        console.log('AppState initialized');
    }

    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Update state and notify listeners
     */
    setState(updates) {
        const oldState = { ...this.state };
        this.state = this.deepMerge(this.state, updates);
        
        // Save to localStorage
        this.saveToLocalStorage();
        
        // Notify listeners
        this.notifyListeners(oldState, this.state);
        
        console.log('State updated:', updates);
    }

    /**
     * Subscribe to state changes
     */
    subscribe(key, callback) {
        if (!this.listeners[key]) {
            this.listeners[key] = [];
        }
        this.listeners[key].push(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners[key] = this.listeners[key].filter(cb => cb !== callback);
        };
    }

    /**
     * Notify all listeners of state changes
     */
    notifyListeners(oldState, newState) {
        Object.keys(this.listeners).forEach(key => {
            if (this.hasChanged(oldState, newState, key)) {
                this.listeners[key].forEach(callback => {
                    try {
                        callback(newState, oldState);
                    } catch (error) {
                        console.error(`Error in state listener for ${key}:`, error);
                    }
                });
            }
        });
    }

    /**
     * Check if a specific part of state has changed
     */
    hasChanged(oldState, newState, key) {
        const keys = key.split('.');
        let oldValue = oldState;
        let newValue = newState;
        
        for (const k of keys) {
            oldValue = oldValue?.[k];
            newValue = newValue?.[k];
        }
        
        return JSON.stringify(oldValue) !== JSON.stringify(newValue);
    }

    /**
     * Deep merge objects
     */
    deepMerge(target, source) {
        const result = { ...target };
        
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = this.deepMerge(target[key] || {}, source[key]);
            } else {
                result[key] = source[key];
            }
        }
        
        return result;
    }

    /**
     * Load data from API and update state
     */
    async loadData() {
        try {
            console.log('Loading data from API...');
            
            // Load all core data in parallel
            const [personTypes, locations, persons, currentAttendance] = await Promise.all([
                this.api.getPersonTypes(),
                this.api.getLocations(),
                this.api.getPersons(),
                this.api.getCurrentAttendance()
            ]);

            // Update state with loaded data
            this.setState({
                personTypes: personTypes.data || [],
                locations: locations.data || [],
                persons: persons.data || [],
                currentAttendance: currentAttendance.data || []
            });

            // Calculate statistics
            this.updateStatistics();
            
            console.log('Data loaded successfully');
            return true;
        } catch (error) {
            console.error('Failed to load data:', error);
            throw error;
        }
    }

    /**
     * Update statistics based on current data
     */
    updateStatistics() {
        const { personTypes, locations, persons, currentAttendance } = this.state;
        
        const locationOccupancy = {};
        locations.forEach(location => {
            locationOccupancy[location.code] = {
                current: location.current_occupancy || 0,
                capacity: location.capacity || 0,
                percentage: location.capacity ? Math.round((location.current_occupancy / location.capacity) * 100) : 0
            };
        });

        this.setState({
            stats: {
                totalPersons: persons.length,
                totalLocations: locations.length,
                currentlyCheckedIn: currentAttendance.length,
                todayAttendance: currentAttendance.length, // Simplified for now
                locationOccupancy
            }
        });
    }

    /**
     * Authentication methods
     */
    setAuthenticated(userData) {
        this.setState({
            user: {
                ...userData,
                isAuthenticated: true
            }
        });
    }

    logout() {
        this.setState({
            user: {
                uid: null,
                username: '',
                role: 'user',
                permissions: [],
                isAuthenticated: false
            },
            connection: {
                isConnected: false,
                url: '',
                database: '',
                useMockData: false
            }
        });
        localStorage.removeItem('attendanceAppState');
    }

    /**
     * UI state methods
     */
    setCurrentView(view) {
        this.setState({
            ui: { ...this.state.ui, currentView: view }
        });
    }

    setSelectedLocation(location) {
        this.setState({
            ui: { ...this.state.ui, selectedLocation: location }
        });
    }

    setSelectedPerson(person) {
        this.setState({
            ui: { ...this.state.ui, selectedPerson: person }
        });
    }

    toggleSidebar() {
        this.setState({
            ui: { ...this.state.ui, sidebarCollapsed: !this.state.ui.sidebarCollapsed }
        });
    }

    /**
     * Filter methods
     */
    setFilters(filters) {
        this.setState({
            filters: { ...this.state.filters, ...filters }
        });
    }

    setDateRange(from, to) {
        this.setState({
            filters: {
                ...this.state.filters,
                dateRange: { from, to }
            }
        });
    }

    /**
     * Data manipulation methods
     */
    addPersonType(personType) {
        this.setState({
            personTypes: [...this.state.personTypes, personType]
        });
    }

    updatePersonType(id, updates) {
        this.setState({
            personTypes: this.state.personTypes.map(pt => 
                pt.id === id ? { ...pt, ...updates } : pt
            )
        });
    }

    removePersonType(id) {
        this.setState({
            personTypes: this.state.personTypes.filter(pt => pt.id !== id)
        });
    }

    addLocation(location) {
        this.setState({
            locations: [...this.state.locations, location]
        });
    }

    updateLocation(id, updates) {
        this.setState({
            locations: this.state.locations.map(loc => 
                loc.id === id ? { ...loc, ...updates } : loc
            )
        });
    }

    removeLocation(id) {
        this.setState({
            locations: this.state.locations.filter(loc => loc.id !== id)
        });
    }

    addPerson(person) {
        this.setState({
            persons: [...this.state.persons, person]
        });
    }

    updatePerson(id, updates) {
        this.setState({
            persons: this.state.persons.map(person => 
                person.id === id ? { ...person, ...updates } : person
            )
        });
    }

    removePerson(id) {
        this.setState({
            persons: this.state.persons.filter(person => person.id !== id)
        });
    }

    /**
     * Local storage methods
     */
    saveToLocalStorage() {
        try {
            const stateToSave = {
                user: this.state.user,
                connection: this.state.connection,
                ui: this.state.ui,
                filters: this.state.filters
            };
            localStorage.setItem('attendanceAppState', JSON.stringify(stateToSave));
        } catch (error) {
            console.error('Failed to save state to localStorage:', error);
        }
    }

    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('attendanceAppState');
            if (saved) {
                const parsedState = JSON.parse(saved);
                this.state = this.deepMerge(this.state, parsedState);
            }
        } catch (error) {
            console.error('Failed to load state from localStorage:', error);
        }
    }
}

// Create global instance
window.appState = new AppState();

// Export for use in other modules
window.AppState = AppState;
