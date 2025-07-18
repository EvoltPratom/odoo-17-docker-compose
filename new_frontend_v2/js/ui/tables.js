/**
 * Table Helper Functions
 * Utilities for creating and managing data tables
 */

const TableHelpers = {
    /**
     * Create a data table
     */
    createTable(data, columns, options = {}) {
        const {
            className = 'data-table',
            sortable = true,
            searchable = true,
            pagination = false,
            pageSize = 20
        } = options;

        let html = `<table class="${className}">`;
        
        // Header
        html += '<thead><tr>';
        columns.forEach(col => {
            const sortIcon = sortable ? '<i class="fas fa-sort"></i>' : '';
            html += `<th data-column="${col.key}" ${sortable ? 'class="sortable"' : ''}>${col.label} ${sortIcon}</th>`;
        });
        html += '</tr></thead>';
        
        // Body
        html += '<tbody>';
        data.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = this.getCellValue(row, col);
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody>';
        
        html += '</table>';
        
        return html;
    },

    /**
     * Get cell value with formatting
     */
    getCellValue(row, column) {
        let value = this.getNestedValue(row, column.key);
        
        if (column.formatter) {
            return column.formatter(value, row);
        }
        
        if (value === null || value === undefined) {
            return '-';
        }
        
        return Utils.sanitizeHtml(value.toString());
    },

    /**
     * Get nested object value
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    },

    /**
     * Common formatters
     */
    formatters: {
        date: (value) => value ? Utils.formatDate(value, 'DD/MM/YYYY') : '-',
        datetime: (value) => value ? Utils.formatDate(value, 'DD/MM/YYYY HH:mm') : '-',
        time: (value) => value ? Utils.formatDate(value, 'HH:mm') : '-',
        duration: (value) => value ? Utils.formatDuration(value) : '-',
        badge: (value, className = 'badge-secondary') => `<span class="badge ${className}">${value}</span>`,
        boolean: (value) => value ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-danger"></i>',
        actions: (value, row, actions = []) => {
            return actions.map(action => 
                `<button class="btn btn-sm ${action.className}" data-action="${action.action}" data-id="${row.id}">
                    <i class="${action.icon}"></i> ${action.label}
                </button>`
            ).join(' ');
        }
    }
};

// Export for use in other modules
window.TableHelpers = TableHelpers;
