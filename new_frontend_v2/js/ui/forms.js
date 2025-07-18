/**
 * Form Helper Functions
 * Utilities for form handling and validation
 */

const FormHelpers = {
    /**
     * Create form field HTML
     */
    createField(field, value = '') {
        const {
            name,
            label,
            type = 'text',
            required = false,
            options = [],
            placeholder = '',
            help = '',
            className = 'form-control'
        } = field;

        let inputHtml = '';
        
        switch (type) {
            case 'select':
                const optionsHtml = options.map(opt => 
                    `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
                ).join('');
                inputHtml = `<select class="${className}" name="${name}" ${required ? 'required' : ''}>${optionsHtml}</select>`;
                break;
            
            case 'textarea':
                inputHtml = `<textarea class="${className}" name="${name}" placeholder="${placeholder}" ${required ? 'required' : ''}>${value}</textarea>`;
                break;
            
            case 'checkbox':
                inputHtml = `
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" name="${name}" ${value ? 'checked' : ''}>
                        <label class="form-check-label">${label}</label>
                    </div>
                `;
                break;
            
            default:
                inputHtml = `<input type="${type}" class="${className}" name="${name}" value="${value}" placeholder="${placeholder}" ${required ? 'required' : ''}>`;
        }

        if (type === 'checkbox') {
            return `
                <div class="form-group">
                    ${inputHtml}
                    ${help ? `<small class="text-muted">${Utils.sanitizeHtml(help)}</small>` : ''}
                </div>
            `;
        }

        return `
            <div class="form-group">
                <label class="form-label">
                    ${Utils.sanitizeHtml(label)}
                    ${required ? '<span class="text-danger">*</span>' : ''}
                </label>
                ${inputHtml}
                ${help ? `<small class="text-muted">${Utils.sanitizeHtml(help)}</small>` : ''}
            </div>
        `;
    },

    /**
     * Get form data as object
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Handle checkboxes
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            data[checkbox.name] = checkbox.checked;
        });
        
        return data;
    },

    /**
     * Validate form fields
     */
    validateForm(form, fields) {
        let isValid = true;
        
        // Clear previous errors
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });

        // Validate each field
        fields.forEach(field => {
            if (field.required) {
                const input = form.querySelector(`[name="${field.name}"]`);
                if (input && !input.value.trim()) {
                    this.showFieldError(input, `${field.label} is required`);
                    isValid = false;
                }
            }
            
            // Custom validation
            if (field.validate) {
                const input = form.querySelector(`[name="${field.name}"]`);
                if (input) {
                    const error = field.validate(input.value);
                    if (error) {
                        this.showFieldError(input, error);
                        isValid = false;
                    }
                }
            }
        });

        return isValid;
    },

    /**
     * Show field error
     */
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        const error = document.createElement('div');
        error.className = 'invalid-feedback';
        error.textContent = message;
        input.parentNode.appendChild(error);
    }
};

// Export for use in other modules
window.FormHelpers = FormHelpers;
