/**
 * Settings Component
 * Application settings and configuration
 */

class SettingsComponent {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        console.log('Initializing Settings component...');
        this.isInitialized = true;
    }

    async render() {
        console.log('Rendering Settings...');
        
        const container = document.getElementById('settingsView');
        if (!container) return;
        
        container.innerHTML = `
            <div class="settings-container">
                <h2>Settings</h2>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4>Connection Settings</h4>
                            </div>
                            <div class="card-body">
                                <div id="connectionInfo">
                                    <!-- Connection info will be loaded here -->
                                </div>
                                <button class="btn btn-outline-secondary" id="changeConnection">
                                    <i class="fas fa-edit"></i> Change Connection
                                </button>
                            </div>
                        </div>
                        
                        <div class="card mt-4">
                            <div class="card-header">
                                <h4>User Preferences</h4>
                            </div>
                            <div class="card-body">
                                <div class="form-group">
                                    <label>Theme</label>
                                    <select class="form-control" id="themeSelect">
                                        <option value="light">Light</option>
                                        <option value="dark">Dark</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Auto-refresh Interval (seconds)</label>
                                    <select class="form-control" id="refreshInterval">
                                        <option value="15">15 seconds</option>
                                        <option value="30">30 seconds</option>
                                        <option value="60">1 minute</option>
                                        <option value="300">5 minutes</option>
                                    </select>
                                </div>
                                
                                <button class="btn btn-primary" id="savePreferences">
                                    <i class="fas fa-save"></i> Save Preferences
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4>System Information</h4>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm">
                                    <tr>
                                        <td><strong>Application:</strong></td>
                                        <td>Extended Attendance System</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Version:</strong></td>
                                        <td>2.0.0</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Build Date:</strong></td>
                                        <td>${new Date().toLocaleDateString()}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Browser:</strong></td>
                                        <td>${navigator.userAgent.split(' ')[0]}</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        
                        <div class="card mt-4">
                            <div class="card-header">
                                <h4>Data Management</h4>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <button class="btn btn-outline-info" id="exportData">
                                        <i class="fas fa-download"></i> Export All Data
                                    </button>
                                    <button class="btn btn-outline-warning" id="clearCache">
                                        <i class="fas fa-trash"></i> Clear Cache
                                    </button>
                                    <button class="btn btn-outline-danger" id="resetApp">
                                        <i class="fas fa-redo"></i> Reset Application
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.loadConnectionInfo();
        this.loadPreferences();
    }

    setupEventListeners() {
        // Change connection
        const changeConnectionBtn = document.getElementById('changeConnection');
        if (changeConnectionBtn) {
            changeConnectionBtn.addEventListener('click', () => this.changeConnection());
        }

        // Save preferences
        const savePrefsBtn = document.getElementById('savePreferences');
        if (savePrefsBtn) {
            savePrefsBtn.addEventListener('click', () => this.savePreferences());
        }

        // Data management buttons
        const exportBtn = document.getElementById('exportData');
        const clearCacheBtn = document.getElementById('clearCache');
        const resetBtn = document.getElementById('resetApp');

        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => this.clearCache());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetApplication());
        }
    }

    loadConnectionInfo() {
        const state = appState.getState();
        const container = document.getElementById('connectionInfo');
        
        if (container) {
            container.innerHTML = `
                <table class="table table-sm">
                    <tr>
                        <td><strong>Server URL:</strong></td>
                        <td>${state.connection.url || 'Not connected'}</td>
                    </tr>
                    <tr>
                        <td><strong>Database:</strong></td>
                        <td>${state.connection.database || 'Not connected'}</td>
                    </tr>
                    <tr>
                        <td><strong>Username:</strong></td>
                        <td>${state.user.username || 'Not logged in'}</td>
                    </tr>
                    <tr>
                        <td><strong>Status:</strong></td>
                        <td>
                            <span class="badge ${state.connection.isConnected ? 'badge-success' : 'badge-danger'}">
                                ${state.connection.isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                            ${state.connection.useMockData ? '<span class="badge badge-warning">Mock Data</span>' : ''}
                        </td>
                    </tr>
                </table>
            `;
        }
    }

    loadPreferences() {
        const state = appState.getState();
        
        // Load theme
        const themeSelect = document.getElementById('themeSelect');
        if (themeSelect) {
            themeSelect.value = state.ui.theme || 'light';
        }

        // Load refresh interval
        const refreshSelect = document.getElementById('refreshInterval');
        if (refreshSelect) {
            const interval = Constants.DEFAULTS.REFRESH_INTERVAL / 1000;
            refreshSelect.value = interval.toString();
        }
    }

    changeConnection() {
        modalManager.confirm({
            title: 'Change Connection',
            message: 'This will log you out and return to the login screen. Continue?',
            confirmText: 'Continue',
            onConfirm: () => {
                appState.logout();
                window.location.reload();
            }
        });
    }

    savePreferences() {
        const theme = document.getElementById('themeSelect').value;
        const refreshInterval = parseInt(document.getElementById('refreshInterval').value) * 1000;
        
        // Apply theme
        document.documentElement.dataset.theme = theme;
        localStorage.setItem('attendanceTheme', theme);
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
        
        // Save to state
        appState.setState({
            ui: { ...appState.getState().ui, theme }
        });
        
        // Update refresh interval (would need to be implemented in dashboard)
        Constants.DEFAULTS.REFRESH_INTERVAL = refreshInterval;
        
        Utils.showToast('Preferences saved successfully', 'success');
    }

    async exportData() {
        const loadingId = modalManager.showLoading('Exporting data...');
        
        try {
            const state = appState.getState();
            const exportData = {
                timestamp: new Date().toISOString(),
                personTypes: state.personTypes,
                locations: state.locations,
                persons: state.persons,
                currentAttendance: state.currentAttendance
            };
            
            const filename = `attendance_data_export_${new Date().toISOString().split('T')[0]}.json`;
            Utils.downloadAsFile(JSON.stringify(exportData, null, 2), filename, 'application/json');
            
            Utils.showToast('Data exported successfully', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            Utils.showToast('Export failed', 'error');
        } finally {
            modalManager.hideLoading();
        }
    }

    clearCache() {
        modalManager.confirm({
            title: 'Clear Cache',
            message: 'This will clear all cached data and reload from the server. Continue?',
            confirmText: 'Clear Cache',
            onConfirm: async () => {
                const loadingId = modalManager.showLoading('Clearing cache...');
                
                try {
                    // Clear localStorage
                    localStorage.removeItem('attendanceAppState');
                    
                    // Reload data
                    await appState.loadData();
                    
                    Utils.showToast('Cache cleared successfully', 'success');
                } catch (error) {
                    console.error('Failed to clear cache:', error);
                    Utils.showToast('Failed to clear cache', 'error');
                } finally {
                    modalManager.hideLoading();
                }
            }
        });
    }

    resetApplication() {
        modalManager.confirm({
            title: 'Reset Application',
            message: 'This will reset all settings and log you out. You will need to reconnect. Continue?',
            confirmText: 'Reset',
            onConfirm: () => {
                // Clear all localStorage
                localStorage.clear();
                
                // Reload page
                window.location.reload();
            }
        });
    }
}

window.SettingsComponent = SettingsComponent;
