/**
 * Application Constants
 * Centralized constants for the Extended Attendance System
 */

const Constants = {
    // Application info
    APP_NAME: 'Extended Attendance System',
    APP_VERSION: '2.0.0',
    
    // API endpoints
    API_ENDPOINTS: {
        PERSON_TYPES: '/api/attendance/person-types',
        LOCATIONS: '/api/attendance/locations',
        PERSONS: '/api/attendance/persons',
        ATTENDANCE: '/api/attendance',
        CHECK_IN: '/api/attendance/check-in',
        CHECK_OUT: '/api/attendance/check-out',
        CURRENT: '/api/attendance/current',
        RECORDS: '/api/attendance/records',
        REPORT: '/api/attendance/report'
    },

    // User roles and permissions
    USER_ROLES: {
        USER: 'user',
        OFFICER: 'officer',
        MANAGER: 'manager'
    },

    PERMISSIONS: {
        VIEW_DASHBOARD: 'view_dashboard',
        MANAGE_PERSONS: 'manage_persons',
        MANAGE_LOCATIONS: 'manage_locations',
        MANAGE_PERSON_TYPES: 'manage_person_types',
        RECORD_ATTENDANCE: 'record_attendance',
        VIEW_REPORTS: 'view_reports',
        EXPORT_DATA: 'export_data',
        SYSTEM_ADMIN: 'system_admin'
    },

    // Person type codes
    PERSON_TYPES: {
        ADMIN: 'ADMIN',
        OWNER: 'OWNER',
        EMPLOYEE: 'EMP',
        STUDENT: 'STU',
        GUEST: 'GST'
    },

    // Access levels
    ACCESS_LEVELS: {
        BASIC: 'basic',
        STANDARD: 'standard',
        FULL: 'full',
        RESTRICTED: 'restricted'
    },

    // Attendance states
    ATTENDANCE_STATES: {
        CHECKED_IN: 'checked_in',
        CHECKED_OUT: 'checked_out',
        OVERTIME: 'overtime',
        INCOMPLETE: 'incomplete'
    },

    // Device types
    DEVICE_TYPES: {
        RFID: 'rfid',
        BIOMETRIC: 'biometric',
        QR: 'qr',
        MANUAL: 'manual',
        MOBILE: 'mobile'
    },

    // UI views
    VIEWS: {
        DASHBOARD: 'dashboard',
        ATTENDANCE: 'attendance',
        PERSONS: 'persons',
        LOCATIONS: 'locations',
        PERSON_TYPES: 'person-types',
        REPORTS: 'reports',
        SETTINGS: 'settings'
    },

    // Colors for UI elements
    COLORS: {
        PRIMARY: '#3498db',
        SUCCESS: '#2ecc71',
        WARNING: '#f39c12',
        DANGER: '#e74c3c',
        INFO: '#17a2b8',
        LIGHT: '#f8f9fa',
        DARK: '#343a40',
        SECONDARY: '#6c757d'
    },

    // Person type colors
    PERSON_TYPE_COLORS: {
        ADMIN: '#e74c3c',
        OWNER: '#9b59b6',
        EMP: '#3498db',
        STU: '#2ecc71',
        GST: '#f39c12'
    },

    // Status colors
    STATUS_COLORS: {
        checked_in: '#2ecc71',
        checked_out: '#95a5a6',
        overtime: '#f39c12',
        incomplete: '#e74c3c',
        active: '#2ecc71',
        inactive: '#95a5a6'
    },

    // Occupancy status
    OCCUPANCY_STATUS: {
        LOW: 'low',
        MEDIUM: 'medium',
        HIGH: 'high',
        CRITICAL: 'critical'
    },

    // Date formats
    DATE_FORMATS: {
        DATE: 'YYYY-MM-DD',
        DATETIME: 'YYYY-MM-DD HH:mm',
        TIME: 'HH:mm',
        DISPLAY_DATE: 'DD/MM/YYYY',
        DISPLAY_DATETIME: 'DD/MM/YYYY HH:mm'
    },

    // Validation rules
    VALIDATION: {
        MIN_PASSWORD_LENGTH: 6,
        MAX_NAME_LENGTH: 100,
        MAX_DESCRIPTION_LENGTH: 500,
        PHONE_PATTERN: /^[\+]?[1-9][\d]{0,15}$/,
        EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        CODE_PATTERN: /^[A-Z0-9_]+$/
    },

    // Local storage keys
    STORAGE_KEYS: {
        APP_STATE: 'attendanceAppState',
        USER_PREFERENCES: 'attendanceUserPrefs',
        THEME: 'attendanceTheme'
    },

    // Animation durations (ms)
    ANIMATIONS: {
        FAST: 150,
        NORMAL: 300,
        SLOW: 500
    },

    // Pagination
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 20,
        PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
    },

    // File upload
    FILE_UPLOAD: {
        MAX_SIZE: 5 * 1024 * 1024, // 5MB
        ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
        ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.gif']
    },

    // Toast notification types
    TOAST_TYPES: {
        SUCCESS: 'success',
        ERROR: 'error',
        WARNING: 'warning',
        INFO: 'info'
    },

    // Modal sizes
    MODAL_SIZES: {
        SMALL: 'modal-sm',
        MEDIUM: 'modal-md',
        LARGE: 'modal-lg',
        EXTRA_LARGE: 'modal-xl'
    },

    // Chart types
    CHART_TYPES: {
        LINE: 'line',
        BAR: 'bar',
        PIE: 'pie',
        DOUGHNUT: 'doughnut',
        AREA: 'area'
    },

    // Export formats
    EXPORT_FORMATS: {
        CSV: 'csv',
        EXCEL: 'xlsx',
        PDF: 'pdf',
        JSON: 'json'
    },

    // Time intervals
    TIME_INTERVALS: {
        MINUTE: 60 * 1000,
        HOUR: 60 * 60 * 1000,
        DAY: 24 * 60 * 60 * 1000,
        WEEK: 7 * 24 * 60 * 60 * 1000,
        MONTH: 30 * 24 * 60 * 60 * 1000
    },

    // Default values
    DEFAULTS: {
        LOCATION_CAPACITY: 0,
        MAX_DURATION_HOURS: 8,
        REFRESH_INTERVAL: 30000, // 30 seconds
        SEARCH_DEBOUNCE: 300,
        TOAST_DURATION: 3000
    },

    // Error messages
    ERROR_MESSAGES: {
        CONNECTION_FAILED: 'Failed to connect to the server',
        AUTHENTICATION_FAILED: 'Authentication failed',
        PERMISSION_DENIED: 'Permission denied',
        VALIDATION_FAILED: 'Validation failed',
        NETWORK_ERROR: 'Network error occurred',
        UNKNOWN_ERROR: 'An unknown error occurred'
    },

    // Success messages
    SUCCESS_MESSAGES: {
        CONNECTED: 'Successfully connected',
        SAVED: 'Successfully saved',
        DELETED: 'Successfully deleted',
        CHECKED_IN: 'Successfully checked in',
        CHECKED_OUT: 'Successfully checked out',
        EXPORTED: 'Data exported successfully'
    },

    // Field types for custom fields
    FIELD_TYPES: {
        CHAR: 'char',
        TEXT: 'text',
        INTEGER: 'integer',
        FLOAT: 'float',
        BOOLEAN: 'boolean',
        DATE: 'date',
        DATETIME: 'datetime',
        SELECTION: 'selection'
    },

    // Weekdays
    WEEKDAYS: {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    },

    // Icons for different elements
    ICONS: {
        DASHBOARD: 'fas fa-tachometer-alt',
        ATTENDANCE: 'fas fa-clock',
        PERSONS: 'fas fa-users',
        LOCATIONS: 'fas fa-map-marker-alt',
        PERSON_TYPES: 'fas fa-tags',
        REPORTS: 'fas fa-chart-bar',
        SETTINGS: 'fas fa-cog',
        CHECK_IN: 'fas fa-sign-in-alt',
        CHECK_OUT: 'fas fa-sign-out-alt',
        ADD: 'fas fa-plus',
        EDIT: 'fas fa-edit',
        DELETE: 'fas fa-trash',
        SEARCH: 'fas fa-search',
        FILTER: 'fas fa-filter',
        EXPORT: 'fas fa-download',
        REFRESH: 'fas fa-sync-alt'
    }
};

// Freeze the constants to prevent modification
Object.freeze(Constants);

// Export for use in other modules
window.Constants = Constants;
