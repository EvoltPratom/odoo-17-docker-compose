/**
 * Utility Functions for Extended Attendance System
 * Common helper functions used throughout the application
 */

const Utils = {
    /**
     * Format date and time
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        if (!date) return '';
        
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        switch (format) {
            case 'YYYY-MM-DD':
                return `${year}-${month}-${day}`;
            case 'DD/MM/YYYY':
                return `${day}/${month}/${year}`;
            case 'YYYY-MM-DD HH:mm':
                return `${year}-${month}-${day} ${hours}:${minutes}`;
            case 'DD/MM/YYYY HH:mm':
                return `${day}/${month}/${year} ${hours}:${minutes}`;
            case 'HH:mm':
                return `${hours}:${minutes}`;
            case 'HH:mm:ss':
                return `${hours}:${minutes}:${seconds}`;
            default:
                return d.toLocaleDateString();
        }
    },

    /**
     * Format duration from minutes or hours
     */
    formatDuration(hours) {
        if (!hours || hours === 0) return '0h 0m';
        
        const h = Math.floor(hours);
        const m = Math.round((hours - h) * 60);
        
        if (h === 0) return `${m}m`;
        if (m === 0) return `${h}h`;
        return `${h}h ${m}m`;
    },

    /**
     * Calculate time difference
     */
    timeDifference(start, end = null) {
        const startTime = new Date(start);
        const endTime = end ? new Date(end) : new Date();
        const diffMs = endTime - startTime;
        const diffHours = diffMs / (1000 * 60 * 60);
        return diffHours;
    },

    /**
     * Debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function calls
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    /**
     * Validate email
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate phone number
     */
    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    },

    /**
     * Sanitize HTML
     */
    sanitizeHtml(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    },

    /**
     * Copy to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${this.sanitizeHtml(message)}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    },

    /**
     * Get icon for toast type
     */
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Show loading spinner
     */
    showLoading(element, text = 'Loading...') {
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <span>${text}</span>
            </div>
        `;
        
        if (element) {
            element.style.position = 'relative';
            element.appendChild(loader);
        } else {
            document.body.appendChild(loader);
        }
        
        return loader;
    },

    /**
     * Hide loading spinner
     */
    hideLoading(loader) {
        if (loader && loader.parentNode) {
            loader.parentNode.removeChild(loader);
        }
    },

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Get color for person type
     */
    getPersonTypeColor(personType) {
        const colors = {
            'ADMIN': '#e74c3c',
            'OWNER': '#9b59b6',
            'EMP': '#3498db',
            'STU': '#2ecc71',
            'GST': '#f39c12'
        };
        return colors[personType] || '#95a5a6';
    },

    /**
     * Get status color
     */
    getStatusColor(status) {
        const colors = {
            'checked_in': '#2ecc71',
            'checked_out': '#95a5a6',
            'overtime': '#f39c12',
            'incomplete': '#e74c3c'
        };
        return colors[status] || '#95a5a6';
    },

    /**
     * Calculate occupancy percentage
     */
    calculateOccupancy(current, capacity) {
        if (!capacity || capacity === 0) return 0;
        return Math.round((current / capacity) * 100);
    },

    /**
     * Get occupancy status
     */
    getOccupancyStatus(percentage) {
        if (percentage >= 90) return 'critical';
        if (percentage >= 75) return 'high';
        if (percentage >= 50) return 'medium';
        return 'low';
    },

    /**
     * Sort array by multiple fields
     */
    sortBy(array, ...fields) {
        return array.sort((a, b) => {
            for (const field of fields) {
                const [key, direction = 'asc'] = field.split(':');
                const aVal = this.getNestedValue(a, key);
                const bVal = this.getNestedValue(b, key);
                
                if (aVal < bVal) return direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            }
            return 0;
        });
    },

    /**
     * Get nested object value
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    },

    /**
     * Filter array by search term
     */
    filterBySearch(array, searchTerm, fields) {
        if (!searchTerm) return array;
        
        const term = searchTerm.toLowerCase();
        return array.filter(item => {
            return fields.some(field => {
                const value = this.getNestedValue(item, field);
                return value && value.toString().toLowerCase().includes(term);
            });
        });
    },

    /**
     * Group array by field
     */
    groupBy(array, field) {
        return array.reduce((groups, item) => {
            const key = this.getNestedValue(item, field);
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(item);
            return groups;
        }, {});
    },

    /**
     * Download data as file
     */
    downloadAsFile(data, filename, type = 'application/json') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },

    /**
     * Export data as CSV
     */
    exportAsCSV(data, filename, headers = null) {
        if (!data.length) return;
        
        const csvHeaders = headers || Object.keys(data[0]);
        const csvRows = [csvHeaders.join(',')];
        
        data.forEach(row => {
            const values = csvHeaders.map(header => {
                const value = row[header] || '';
                return `"${value.toString().replace(/"/g, '""')}"`;
            });
            csvRows.push(values.join(','));
        });
        
        this.downloadAsFile(csvRows.join('\n'), filename, 'text/csv');
    }
};

// Export for use in other modules
window.Utils = Utils;
