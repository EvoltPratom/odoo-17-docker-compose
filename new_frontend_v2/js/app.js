/**
 * Main Application Controller
 * Handles application initialization, routing, and global state management
 */

class ExtendedAttendanceApp {
    constructor() {
        this.api = new ExtendedOdooAPI();
        this.currentView = 'dashboard';
        this.isAuthenticated = false;
        this.components = {};
        
        // Bind methods
        this.handleLogin = this.handleLogin.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
        this.handleNavigation = this.handleNavigation.bind(this);
        this.handleRefresh = this.handleRefresh.bind(this);
        this.toggleSidebar = this.toggleSidebar.bind(this);
        this.toggleTheme = this.toggleTheme.bind(this);
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Extended Attendance System...');
        
        try {
            // Initialize state management
            appState.init(this.api);
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Check for saved authentication
            await this.checkSavedAuth();
            
            // Initialize UI
            this.initializeUI();
            
            console.log('Application initialized successfully');
        } catch (error) {
            console.error('Failed to initialize application:', error);
            Utils.showToast('Failed to initialize application', 'error');
        }
    }

    /**
     * Set up global event listeners
     */
    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin);
        }

        // Navigation
        document.addEventListener('click', (e) => {
            const navItem = e.target.closest('[data-view]');
            if (navItem) {
                e.preventDefault();
                this.handleNavigation(navItem.dataset.view);
            }
        });

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', this.toggleSidebar);
        }

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme);
        }

        // Refresh data
        const refreshData = document.getElementById('refreshData');
        if (refreshData) {
            refreshData.addEventListener('click', this.handleRefresh);
        }

        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', this.handleLogout);
        }

        // Subscribe to state changes
        appState.subscribe('user.isAuthenticated', (newState) => {
            this.isAuthenticated = newState.user.isAuthenticated;
            this.updateAuthUI();
        });

        appState.subscribe('ui.currentView', (newState) => {
            this.currentView = newState.ui.currentView;
            this.updateViewUI();
        });

        // Handle window resize
        window.addEventListener('resize', Utils.debounce(() => {
            this.handleResize();
        }, 250));
    }

    /**
     * Check for saved authentication
     */
    async checkSavedAuth() {
        const state = appState.getState();
        if (state.connection.isConnected && state.user.isAuthenticated) {
            try {
                // Try to reconnect with saved credentials
                const result = await this.api.connect(
                    state.connection.url,
                    state.connection.database,
                    state.user.username,
                    'saved' // We don't save passwords
                );
                
                if (result.success) {
                    this.isAuthenticated = true;
                    appState.setAuthenticated({
                        uid: result.uid,
                        username: state.user.username,
                        role: state.user.role || 'user'
                    });
                    
                    await this.loadInitialData();
                }
            } catch (error) {
                console.log('Saved authentication failed, showing login');
                appState.logout();
            }
        }
    }

    /**
     * Handle login form submission
     */
    async handleLogin(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const url = formData.get('odooUrl');
        const database = formData.get('database');
        const username = formData.get('username');
        const password = formData.get('password');

        const loadingId = modalManager.showLoading('Connecting to Odoo...');
        
        try {
            const result = await this.api.connect(url, database, username, password);
            
            if (result.success) {
                // Update connection status
                appState.setState({
                    connection: {
                        isConnected: true,
                        url,
                        database,
                        useMockData: result.mock || false
                    }
                });

                // Set user as authenticated
                appState.setAuthenticated({
                    uid: result.uid,
                    username,
                    role: 'user' // Default role, can be enhanced later
                });

                // Load initial data
                await this.loadInitialData();
                
                Utils.showToast(
                    result.mock ? 'Connected with mock data' : 'Successfully connected to Odoo',
                    'success'
                );
            }
        } catch (error) {
            console.error('Login failed:', error);
            Utils.showToast(`Connection failed: ${error.message}`, 'error');
            this.updateConnectionStatus(false);
        } finally {
            modalManager.hideLoading();
        }
    }

    /**
     * Load initial data after authentication
     */
    async loadInitialData() {
        try {
            console.log('Loading initial data...');
            await appState.loadData();
            console.log('Initial data loaded successfully');
        } catch (error) {
            console.error('Failed to load initial data:', error);
            Utils.showToast('Failed to load data', 'error');
        }
    }

    /**
     * Handle logout
     */
    handleLogout(e) {
        e.preventDefault();
        
        modalManager.confirm({
            title: 'Logout',
            message: 'Are you sure you want to logout?',
            confirmText: 'Logout',
            onConfirm: () => {
                appState.logout();
                this.api = new ExtendedOdooAPI();
                Utils.showToast('Logged out successfully', 'info');
            }
        });
    }

    /**
     * Handle navigation between views
     */
    handleNavigation(viewName) {
        if (this.currentView === viewName) return;
        
        console.log(`Navigating to ${viewName}`);
        appState.setCurrentView(viewName);
        
        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            pageTitle.textContent = this.getViewTitle(viewName);
        }
        
        // Load view component if not already loaded
        this.loadViewComponent(viewName);
    }

    /**
     * Get view title
     */
    getViewTitle(viewName) {
        const titles = {
            dashboard: 'Dashboard',
            attendance: 'Attendance',
            persons: 'Persons',
            locations: 'Locations',
            'person-types': 'Person Types',
            reports: 'Reports',
            settings: 'Settings'
        };
        return titles[viewName] || 'Extended Attendance';
    }

    /**
     * Load view component
     */
    async loadViewComponent(viewName) {
        try {
            // Initialize component if not already done
            if (!this.components[viewName]) {
                switch (viewName) {
                    case 'dashboard':
                        this.components[viewName] = new DashboardComponent();
                        break;
                    case 'attendance':
                        this.components[viewName] = new AttendanceComponent();
                        break;
                    case 'persons':
                        this.components[viewName] = new PersonsComponent();
                        break;
                    case 'locations':
                        this.components[viewName] = new LocationsComponent();
                        break;
                    case 'person-types':
                        this.components[viewName] = new PersonTypesComponent();
                        break;
                    case 'reports':
                        this.components[viewName] = new ReportsComponent();
                        break;
                    case 'settings':
                        this.components[viewName] = new SettingsComponent();
                        break;
                }
                
                if (this.components[viewName]) {
                    await this.components[viewName].init();
                }
            }
            
            // Render the component
            if (this.components[viewName]) {
                await this.components[viewName].render();
            }
        } catch (error) {
            console.error(`Failed to load ${viewName} component:`, error);
            Utils.showToast(`Failed to load ${viewName}`, 'error');
        }
    }

    /**
     * Handle data refresh
     */
    async handleRefresh() {
        if (!this.isAuthenticated) return;
        
        const refreshBtn = document.getElementById('refreshData');
        const originalIcon = refreshBtn.querySelector('i').className;
        
        try {
            refreshBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
            refreshBtn.disabled = true;
            
            await appState.loadData();
            
            // Refresh current view
            if (this.components[this.currentView]) {
                await this.components[this.currentView].render();
            }
            
            Utils.showToast('Data refreshed successfully', 'success');
        } catch (error) {
            console.error('Failed to refresh data:', error);
            Utils.showToast('Failed to refresh data', 'error');
        } finally {
            refreshBtn.querySelector('i').className = originalIcon;
            refreshBtn.disabled = false;
        }
    }

    /**
     * Toggle sidebar
     */
    toggleSidebar() {
        const appContainer = document.getElementById('appContainer');
        const sidebar = document.getElementById('appSidebar');
        
        if (window.innerWidth <= 768) {
            // Mobile: show/hide sidebar overlay
            sidebar.classList.toggle('show');
        } else {
            // Desktop: collapse/expand sidebar
            appContainer.classList.toggle('sidebar-collapsed');
            appState.toggleSidebar();
        }
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');
        
        const currentTheme = html.dataset.theme || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.dataset.theme = newTheme;
        icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        
        // Save theme preference
        localStorage.setItem('attendanceTheme', newTheme);
        
        appState.setState({
            ui: { ...appState.getState().ui, theme: newTheme }
        });
    }

    /**
     * Initialize UI
     */
    initializeUI() {
        // Load saved theme
        const savedTheme = localStorage.getItem('attendanceTheme') || 'light';
        document.documentElement.dataset.theme = savedTheme;
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            icon.className = savedTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
        
        // Update UI based on authentication state
        this.updateAuthUI();
    }

    /**
     * Update authentication UI
     */
    updateAuthUI() {
        const loginSection = document.getElementById('loginSection');
        const appContainer = document.getElementById('appContainer');
        
        if (this.isAuthenticated) {
            loginSection.classList.add('d-none');
            appContainer.classList.remove('d-none');
            this.updateConnectionStatus(true);
            
            // Load dashboard by default
            if (this.currentView === 'dashboard') {
                this.loadViewComponent('dashboard');
            }
        } else {
            loginSection.classList.remove('d-none');
            appContainer.classList.add('d-none');
            this.updateConnectionStatus(false);
        }
    }

    /**
     * Update view UI
     */
    updateViewUI() {
        // Update navigation active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === this.currentView) {
                item.classList.add('active');
            }
        });
        
        // Show/hide view content
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.add('d-none');
        });
        
        const currentViewElement = document.getElementById(`${this.currentView}View`);
        if (currentViewElement) {
            currentViewElement.classList.remove('d-none');
        }
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(connected) {
        const indicators = document.querySelectorAll('.status-indicator');
        const statusTexts = document.querySelectorAll('.status-text');
        
        indicators.forEach(indicator => {
            indicator.classList.toggle('connected', connected);
        });
        
        statusTexts.forEach(text => {
            text.textContent = connected ? 'Connected' : 'Disconnected';
        });
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const sidebar = document.getElementById('appSidebar');
        
        if (window.innerWidth > 768) {
            // Desktop: remove mobile classes
            sidebar.classList.remove('show');
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    window.app = new ExtendedAttendanceApp();
    await window.app.init();
});

// Export for use in other modules
window.ExtendedAttendanceApp = ExtendedAttendanceApp;
