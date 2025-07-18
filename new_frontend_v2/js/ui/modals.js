/**
 * Modal Management System
 * Handles creation and management of modal dialogs
 */

class ModalManager {
    constructor() {
        this.activeModals = new Map();
        this.modalContainer = null;
    }

    init() {
        this.modalContainer = document.getElementById('modalContainer');
        if (!this.modalContainer) {
            this.modalContainer = document.createElement('div');
            this.modalContainer.id = 'modalContainer';
            document.body.appendChild(this.modalContainer);
        }
    }

    /**
     * Create and show a modal
     */
    show(options = {}) {
        const modalId = options.id || Utils.generateId();
        const modal = this.createModal(modalId, options);
        
        this.modalContainer.appendChild(modal);
        this.activeModals.set(modalId, modal);
        
        // Show modal with animation
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Handle escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape' && !options.persistent) {
                this.hide(modalId);
            }
        };
        document.addEventListener('keydown', handleEscape);
        
        // Store cleanup function
        modal._cleanup = () => {
            document.removeEventListener('keydown', handleEscape);
        };
        
        return modalId;
    }

    /**
     * Hide and remove a modal
     */
    hide(modalId) {
        const modal = this.activeModals.get(modalId);
        if (!modal) return;
        
        modal.classList.remove('show');
        
        setTimeout(() => {
            if (modal._cleanup) {
                modal._cleanup();
            }
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            this.activeModals.delete(modalId);
        }, 300);
    }

    /**
     * Create modal element
     */
    createModal(modalId, options) {
        const {
            title = 'Modal',
            body = '',
            size = 'md',
            persistent = false,
            buttons = [],
            onShow = null,
            onHide = null
        } = options;

        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal modal-${size}">
                <div class="modal-header">
                    <h3 class="modal-title">${Utils.sanitizeHtml(title)}</h3>
                    ${!persistent ? '<button class="modal-close" data-action="close"><i class="fas fa-times"></i></button>' : ''}
                </div>
                <div class="modal-body">
                    ${body}
                </div>
                ${buttons.length > 0 ? `
                    <div class="modal-footer">
                        ${buttons.map(btn => this.createButton(btn)).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        // Handle clicks
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay && !persistent) {
                this.hide(modalId);
            }
            
            if (e.target.dataset.action === 'close') {
                this.hide(modalId);
            }
            
            // Handle button clicks
            const button = e.target.closest('[data-button-id]');
            if (button) {
                const buttonId = button.dataset.buttonId;
                const buttonConfig = buttons.find(b => b.id === buttonId);
                if (buttonConfig && buttonConfig.onClick) {
                    const result = buttonConfig.onClick(modalId);
                    if (result !== false && !buttonConfig.keepOpen) {
                        this.hide(modalId);
                    }
                }
            }
        });

        // Call onShow callback
        if (onShow) {
            setTimeout(() => onShow(modalId), 10);
        }

        return overlay;
    }

    /**
     * Create button HTML
     */
    createButton(button) {
        const {
            id = Utils.generateId(),
            text = 'Button',
            className = 'btn btn-secondary',
            icon = null
        } = button;

        return `
            <button class="${className}" data-button-id="${id}">
                ${icon ? `<i class="${icon}"></i>` : ''}
                ${Utils.sanitizeHtml(text)}
            </button>
        `;
    }

    /**
     * Show confirmation dialog
     */
    confirm(options = {}) {
        const {
            title = 'Confirm',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            onConfirm = null,
            onCancel = null
        } = options;

        return new Promise((resolve) => {
            const modalId = this.show({
                title,
                body: `<p>${Utils.sanitizeHtml(message)}</p>`,
                size: 'sm',
                buttons: [
                    {
                        id: 'cancel',
                        text: cancelText,
                        className: 'btn btn-secondary',
                        onClick: () => {
                            if (onCancel) onCancel();
                            resolve(false);
                        }
                    },
                    {
                        id: 'confirm',
                        text: confirmText,
                        className: 'btn btn-danger',
                        onClick: () => {
                            if (onConfirm) onConfirm();
                            resolve(true);
                        }
                    }
                ]
            });
        });
    }

    /**
     * Show alert dialog
     */
    alert(options = {}) {
        const {
            title = 'Alert',
            message = '',
            type = 'info',
            okText = 'OK',
            onOk = null
        } = options;

        const icons = {
            success: 'fas fa-check-circle text-success',
            warning: 'fas fa-exclamation-triangle text-warning',
            error: 'fas fa-exclamation-circle text-danger',
            info: 'fas fa-info-circle text-info'
        };

        return new Promise((resolve) => {
            const modalId = this.show({
                title,
                body: `
                    <div class="text-center">
                        <i class="${icons[type] || icons.info}" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <p>${Utils.sanitizeHtml(message)}</p>
                    </div>
                `,
                size: 'sm',
                buttons: [
                    {
                        id: 'ok',
                        text: okText,
                        className: 'btn btn-primary',
                        onClick: () => {
                            if (onOk) onOk();
                            resolve(true);
                        }
                    }
                ]
            });
        });
    }

    /**
     * Show loading modal
     */
    showLoading(message = 'Loading...') {
        return this.show({
            id: 'loading-modal',
            title: 'Please Wait',
            body: `
                <div class="text-center">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>${Utils.sanitizeHtml(message)}</p>
                </div>
            `,
            size: 'sm',
            persistent: true
        });
    }

    /**
     * Hide loading modal
     */
    hideLoading() {
        this.hide('loading-modal');
    }

    /**
     * Show form modal
     */
    showForm(options = {}) {
        const {
            title = 'Form',
            fields = [],
            data = {},
            onSubmit = null,
            onCancel = null,
            submitText = 'Save',
            cancelText = 'Cancel'
        } = options;

        const formId = Utils.generateId();
        const formHtml = this.createFormHtml(formId, fields, data);

        return new Promise((resolve) => {
            const modalId = this.show({
                title,
                body: formHtml,
                size: 'lg',
                buttons: [
                    {
                        id: 'cancel',
                        text: cancelText,
                        className: 'btn btn-secondary',
                        onClick: () => {
                            if (onCancel) onCancel();
                            resolve(null);
                        }
                    },
                    {
                        id: 'submit',
                        text: submitText,
                        className: 'btn btn-primary',
                        onClick: () => {
                            const formData = this.getFormData(formId);
                            if (this.validateForm(formId, fields)) {
                                if (onSubmit) {
                                    const result = onSubmit(formData);
                                    if (result !== false) {
                                        resolve(formData);
                                        return true;
                                    }
                                    return false;
                                } else {
                                    resolve(formData);
                                    return true;
                                }
                            }
                            return false;
                        }
                    }
                ]
            });
        });
    }

    /**
     * Create form HTML
     */
    createFormHtml(formId, fields, data) {
        const fieldsHtml = fields.map(field => {
            const value = data[field.name] || field.defaultValue || '';
            return this.createFieldHtml(field, value);
        }).join('');

        return `<form id="${formId}">${fieldsHtml}</form>`;
    }

    /**
     * Create field HTML
     */
    createFieldHtml(field, value) {
        const {
            name,
            label,
            type = 'text',
            required = false,
            options = [],
            placeholder = '',
            help = ''
        } = field;

        let inputHtml = '';
        
        switch (type) {
            case 'select':
                const optionsHtml = options.map(opt => 
                    `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
                ).join('');
                inputHtml = `<select class="form-control" name="${name}" ${required ? 'required' : ''}>${optionsHtml}</select>`;
                break;
            
            case 'textarea':
                inputHtml = `<textarea class="form-control" name="${name}" placeholder="${placeholder}" ${required ? 'required' : ''}>${value}</textarea>`;
                break;
            
            case 'checkbox':
                inputHtml = `<input type="checkbox" name="${name}" ${value ? 'checked' : ''}>`;
                break;
            
            default:
                inputHtml = `<input type="${type}" class="form-control" name="${name}" value="${value}" placeholder="${placeholder}" ${required ? 'required' : ''}>`;
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
    }

    /**
     * Get form data
     */
    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};

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
    }

    /**
     * Validate form
     */
    validateForm(formId, fields) {
        const form = document.getElementById(formId);
        if (!form) return false;

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
    }

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
}

// Create global instance
window.modalManager = new ModalManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.modalManager.init();
});

// Export for use in other modules
window.ModalManager = ModalManager;
