/**
 * Person Types Component
 * Manage person types with custom fields and access control
 */

class PersonTypesComponent {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;
        console.log('Initializing Person Types component...');
        this.isInitialized = true;
    }

    async render() {
        console.log('Rendering Person Types...');
        
        const container = document.getElementById('personTypesView');
        if (!container) return;
        
        container.innerHTML = `
            <div class="person-types-container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Person Types Management</h2>
                    <button class="btn btn-primary" id="addPersonTypeBtn">
                        <i class="fas fa-plus"></i> Add Person Type
                    </button>
                </div>

                <div class="card">
                    <div class="card-body">
                        <div id="personTypesList">
                            <!-- Person types will be rendered here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.renderPersonTypesList();
    }

    setupEventListeners() {
        const addBtn = document.getElementById('addPersonTypeBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showPersonTypeModal());
        }
    }

    renderPersonTypesList() {
        const container = document.getElementById('personTypesList');
        if (!container) return;
        
        const state = appState.getState();
        const personTypes = state.personTypes;
        
        if (personTypes.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-tags fa-3x mb-3"></i>
                    <h4>No person types found</h4>
                    <p>Create person types to categorize people in your system.</p>
                </div>
            `;
            return;
        }
        
        const columns = [
            { key: 'name', label: 'Name' },
            { key: 'code', label: 'Code' },
            { key: 'person_count', label: 'Persons' },
            { key: 'default_access_level', label: 'Access Level' },
            { 
                key: 'is_system', 
                label: 'System Type',
                formatter: TableHelpers.formatters.boolean
            },
            {
                key: 'actions',
                label: 'Actions',
                formatter: (value, row) => {
                    const canDelete = !row.is_system;
                    return `
                        <button class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${row.id}">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        ${canDelete ? `
                            <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${row.id}">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        ` : ''}
                    `;
                }
            }
        ];
        
        container.innerHTML = TableHelpers.createTable(personTypes, columns);
        
        // Add event listeners for actions
        container.addEventListener('click', (e) => {
            const button = e.target.closest('[data-action]');
            if (!button) return;
            
            const action = button.dataset.action;
            const id = parseInt(button.dataset.id);
            
            switch (action) {
                case 'edit':
                    this.showPersonTypeModal(id);
                    break;
                case 'delete':
                    this.deletePersonType(id);
                    break;
            }
        });
    }

    async showPersonTypeModal(personTypeId = null) {
        const isEdit = personTypeId !== null;
        const state = appState.getState();
        const personType = isEdit ? state.personTypes.find(pt => pt.id === personTypeId) : {};
        
        const formData = await modalManager.showForm({
            title: isEdit ? 'Edit Person Type' : 'Add New Person Type',
            fields: [
                {
                    name: 'name',
                    label: 'Name',
                    type: 'text',
                    required: true,
                    defaultValue: personType.name || '',
                    placeholder: 'e.g., Employee, Student, Guest'
                },
                {
                    name: 'code',
                    label: 'Code',
                    type: 'text',
                    required: true,
                    defaultValue: personType.code || '',
                    placeholder: 'e.g., EMP, STU, GST',
                    help: 'Unique identifier (uppercase, no spaces)'
                },
                {
                    name: 'description',
                    label: 'Description',
                    type: 'textarea',
                    defaultValue: personType.description || '',
                    placeholder: 'Optional description'
                },
                {
                    name: 'default_access_level',
                    label: 'Default Access Level',
                    type: 'select',
                    options: [
                        { value: 'basic', label: 'Basic' },
                        { value: 'standard', label: 'Standard' },
                        { value: 'full', label: 'Full' },
                        { value: 'restricted', label: 'Restricted' }
                    ],
                    defaultValue: personType.default_access_level || 'basic'
                },
                {
                    name: 'max_duration_hours',
                    label: 'Max Duration (Hours)',
                    type: 'number',
                    defaultValue: personType.max_duration_hours || '',
                    placeholder: 'Optional maximum attendance duration'
                },
                {
                    name: 'requires_approval',
                    label: 'Requires Approval',
                    type: 'checkbox',
                    defaultValue: personType.requires_approval || false
                }
            ],
            submitText: isEdit ? 'Update Person Type' : 'Create Person Type'
        });
        
        if (formData) {
            await this.savePersonType(formData, personTypeId);
        }
    }

    async savePersonType(data, personTypeId = null) {
        const loadingId = modalManager.showLoading(personTypeId ? 'Updating person type...' : 'Creating person type...');
        
        try {
            let result;
            if (personTypeId) {
                result = await window.app.api.updatePersonType(personTypeId, data);
            } else {
                result = await window.app.api.createPersonType(data);
            }
            
            if (result.success) {
                Utils.showToast(
                    personTypeId ? 'Person type updated successfully' : 'Person type created successfully',
                    'success'
                );
                await appState.loadData();
                this.renderPersonTypesList();
            } else {
                throw new Error(result.error || 'Failed to save person type');
            }
        } catch (error) {
            console.error('Failed to save person type:', error);
            Utils.showToast(`Failed to save person type: ${error.message}`, 'error');
        } finally {
            modalManager.hideLoading();
        }
    }

    async deletePersonType(personTypeId) {
        const state = appState.getState();
        const personType = state.personTypes.find(pt => pt.id === personTypeId);
        
        if (!personType) return;
        
        if (personType.is_system) {
            Utils.showToast('System person types cannot be deleted', 'warning');
            return;
        }
        
        const confirmed = await modalManager.confirm({
            title: 'Delete Person Type',
            message: `Are you sure you want to delete "${personType.name}"? This action cannot be undone.`,
            confirmText: 'Delete'
        });
        
        if (confirmed) {
            const loadingId = modalManager.showLoading('Deleting person type...');
            
            try {
                const result = await window.app.api.deletePersonType(personTypeId);
                
                if (result.success) {
                    Utils.showToast('Person type deleted successfully', 'success');
                    await appState.loadData();
                    this.renderPersonTypesList();
                } else {
                    throw new Error(result.error || 'Failed to delete person type');
                }
            } catch (error) {
                console.error('Failed to delete person type:', error);
                Utils.showToast(`Failed to delete person type: ${error.message}`, 'error');
            } finally {
                modalManager.hideLoading();
            }
        }
    }
}

window.PersonTypesComponent = PersonTypesComponent;
