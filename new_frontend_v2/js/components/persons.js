/**
 * Persons Component
 * Manage persons with types, custom fields, and search functionality
 */

class PersonsComponent {
    constructor() {
        this.isInitialized = false;
        this.currentView = 'grid';
        this.searchTerm = '';
    }

    async init() {
        if (this.isInitialized) return;
        console.log('Initializing Persons component...');
        this.isInitialized = true;
    }

    async render() {
        console.log('Rendering Persons...');
        
        const container = document.getElementById('personsView');
        if (!container) return;
        
        container.innerHTML = `
            <div class="persons-container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Persons Management</h2>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-secondary" id="togglePersonView">
                            <i class="fas fa-th" id="personViewIcon"></i>
                        </button>
                        <button class="btn btn-primary" id="addPersonBtn">
                            <i class="fas fa-plus"></i> Add Person
                        </button>
                    </div>
                </div>

                <div class="search-filters">
                    <div class="search-row">
                        <div class="form-group">
                            <input type="text" class="form-control" id="personSearch" 
                                   placeholder="Search persons..." value="${this.searchTerm}">
                        </div>
                        <div class="filter-group">
                            <select class="form-control" id="personTypeFilter">
                                <option value="">All Types</option>
                            </select>
                            <select class="form-control" id="statusFilter">
                                <option value="">All Status</option>
                                <option value="checked_in">Checked In</option>
                                <option value="not_checked_in">Not Checked In</option>
                            </select>
                        </div>
                        <button class="btn btn-outline-secondary" id="clearPersonFilters">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                </div>

                <div id="personsList" class="person-grid">
                    <!-- Persons will be rendered here -->
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.renderPersonsList();
    }

    setupEventListeners() {
        // Add person button
        const addBtn = document.getElementById('addPersonBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showPersonModal());
        }

        // Search input
        const searchInput = document.getElementById('personSearch');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce((e) => {
                this.searchTerm = e.target.value;
                this.renderPersonsList();
            }, 300));
        }
    }

    renderPersonsList() {
        const container = document.getElementById('personsList');
        if (!container) return;
        
        const state = appState.getState();
        let persons = [...state.persons];
        
        // Apply search filter
        if (this.searchTerm) {
            persons = Utils.filterBySearch(persons, this.searchTerm, 
                ['name', 'person_id', 'email', 'phone']);
        }
        
        if (persons.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h4>No persons found</h4>
                    <p>No persons match your current filters.</p>
                    <button class="btn btn-primary" id="addFirstPerson">
                        <i class="fas fa-plus"></i> Add First Person
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = persons.map(person => this.createPersonCard(person)).join('');
    }

    createPersonCard(person) {
        const initials = person.name.split(' ').map(n => n.charAt(0)).join('').toUpperCase();
        const statusClass = person.is_checked_in ? 'online' : '';
        const statusText = person.is_checked_in ? 'Checked In' : 'Not Checked In';
        const locationText = person.current_location ? ` at ${person.current_location.name}` : '';
        
        return `
            <div class="person-card" data-person-id="${person.id}">
                <div class="person-card-header">
                    <div class="person-avatar">
                        ${initials}
                    </div>
                    <h5 class="person-name">${Utils.sanitizeHtml(person.name)}</h5>
                    <div class="person-type">${Utils.sanitizeHtml(person.person_type.name)}</div>
                </div>
                
                <div class="person-card-body">
                    <div class="person-status">
                        <span class="status-dot ${statusClass}"></span>
                        <span>${statusText}${locationText}</span>
                    </div>
                    
                    <div class="person-info">
                        <small class="text-muted">ID: ${Utils.sanitizeHtml(person.person_id)}</small><br>
                        ${person.email ? `<small class="text-muted">${Utils.sanitizeHtml(person.email)}</small>` : ''}
                    </div>
                    
                    <div class="person-actions mt-3">
                        <button class="btn btn-sm btn-outline-primary" data-action="edit">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        ${person.is_checked_in ? 
                            `<button class="btn btn-sm btn-outline-warning" data-action="check-out">
                                <i class="fas fa-sign-out-alt"></i> Check Out
                            </button>` :
                            `<button class="btn btn-sm btn-outline-success" data-action="check-in">
                                <i class="fas fa-sign-in-alt"></i> Check In
                            </button>`
                        }
                    </div>
                </div>
            </div>
        `;
    }

    async showPersonModal(personId = null) {
        const isEdit = personId !== null;
        const state = appState.getState();
        const person = isEdit ? state.persons.find(p => p.id === personId) : {};
        
        const personTypeOptions = state.personTypes.map(pt => ({
            value: pt.id,
            label: pt.name
        }));
        
        const formData = await modalManager.showForm({
            title: isEdit ? 'Edit Person' : 'Add New Person',
            fields: [
                {
                    name: 'name',
                    label: 'Full Name',
                    type: 'text',
                    required: true,
                    defaultValue: person.name || '',
                    placeholder: 'Enter full name'
                },
                {
                    name: 'person_id',
                    label: 'Person ID',
                    type: 'text',
                    required: true,
                    defaultValue: person.person_id || '',
                    placeholder: 'Unique identifier'
                },
                {
                    name: 'person_type_id',
                    label: 'Person Type',
                    type: 'select',
                    options: personTypeOptions,
                    required: true,
                    defaultValue: person.person_type_id || ''
                },
                {
                    name: 'email',
                    label: 'Email',
                    type: 'email',
                    defaultValue: person.email || '',
                    placeholder: 'email@example.com'
                },
                {
                    name: 'phone',
                    label: 'Phone',
                    type: 'tel',
                    defaultValue: person.phone || '',
                    placeholder: '+1234567890'
                }
            ],
            submitText: isEdit ? 'Update Person' : 'Create Person'
        });
        
        if (formData) {
            await this.savePerson(formData, personId);
        }
    }

    async savePerson(data, personId = null) {
        const loadingId = modalManager.showLoading(personId ? 'Updating person...' : 'Creating person...');
        
        try {
            let result;
            if (personId) {
                result = await window.app.api.updatePerson(personId, data);
            } else {
                result = await window.app.api.createPerson(data);
            }
            
            if (result.success) {
                Utils.showToast(
                    personId ? 'Person updated successfully' : 'Person created successfully',
                    'success'
                );
                await appState.loadData();
                this.renderPersonsList();
            } else {
                throw new Error(result.error || 'Failed to save person');
            }
        } catch (error) {
            console.error('Failed to save person:', error);
            Utils.showToast(`Failed to save person: ${error.message}`, 'error');
        } finally {
            modalManager.hideLoading();
        }
    }
}

window.PersonsComponent = PersonsComponent;
