/**
 * DASHBOARD.js - Handles job application list and CRUD operations
 */

class Dashboard {
    constructor() {
        this.jobs = [];
        this.currentPage = 'dashboard';
    }

    async init() {
        this.setupEventListeners();
        await this.loadJobs();
    }

    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });
    }

    handleNavClick(e) {
        const href = e.target.getAttribute('href');
        if (href === '#dashboard') {
            this.currentPage = 'dashboard';
            this.renderDashboard();
        } else if (href === '#analytics') {
            this.currentPage = 'analytics';
            analytics.renderAnalytics();
        }
    }

    async loadJobs(filters = {}) {
        try {
            this.jobs = await api.getJobs(filters);
            this.renderDashboard();
        } catch (error) {
            authManager.showAlert('Failed to load jobs', 'error');
        }
    }

    renderDashboard() {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = `
            <div class="dashboard-header">
                <h2>📊 My Job Applications</h2>
                <button class="btn btn-primary" onclick="dashboard.showAddJobForm()">+ Add New Job</button>
            </div>

            <div class="filters">
                <input 
                    type="text" 
                    id="searchCompany" 
                    placeholder="Search by company..."
                    onchange="dashboard.applyFilters()"
                >
                <select id="statusFilter" onchange="dashboard.applyFilters()">
                    <option value="">All Statuses</option>
                    <option value="applied">Applied</option>
                    <option value="interview">Interview</option>
                    <option value="offer">Offer</option>
                    <option value="rejected">Rejected</option>
                </select>
            </div>

            <div id="jobsContainer"></div>
        `;

        this.displayJobs(this.jobs);
    }

    displayJobs(jobs) {
        const container = document.getElementById('jobsContainer');
        if (jobs.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; margin: 2rem 0;">No jobs yet. Start adding your applications!</p>';
            return;
        }

        container.innerHTML = jobs.map(job => `
            <div class="job-card">
                <div class="job-info">
                    <h3>${job.company}</h3>
                    <p class="job-meta">Role: ${job.role}</p>
                    <p class="job-meta">Applied: ${new Date(job.applied_date).toLocaleDateString()}</p>
                    <span class="status-badge status-${job.status}">${job.status}</span>
                </div>
                <div class="job-actions">
                    <button class="btn btn-primary" onclick="dashboard.showEditJobForm(${job.id})">Edit</button>
                    <button class="btn btn-primary" onclick="dashboard.showHistory(${job.id})">History</button>
                    <button class="btn btn-danger" onclick="dashboard.deleteJob(${job.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }

    showAddJobForm() {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = `
            <div class="card" style="max-width: 600px;">
                <h2 class="card-title">Add New Job Application</h2>
                <form id="jobForm" onsubmit="dashboard.submitJobForm(event)">
                    <div class="form-group">
                        <label>Company *</label>
                        <input type="text" id="formCompany" required>
                    </div>
                    <div class="form-group">
                        <label>Role *</label>
                        <input type="text" id="formRole" required>
                    </div>
                    <div class="form-group">
                        <label>Status *</label>
                        <select id="formStatus" required>
                            <option value="applied">Applied</option>
                            <option value="interview">Interview</option>
                            <option value="offer">Offer</option>
                            <option value="rejected">Rejected</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Applied Date *</label>
                        <input type="date" id="formDate" required>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="formNotes"></textarea>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn btn-success">Save Job</button>
                        <button type="button" class="btn" style="background-color: #6c757d; color: white;" onclick="dashboard.renderDashboard()">Cancel</button>
                    </div>
                </form>
            </div>
        `;

        // Set today's date as default
        document.getElementById('formDate').valueAsDate = new Date();
    }

    async submitJobForm(e) {
        e.preventDefault();
        const data = {
            company: document.getElementById('formCompany').value,
            role: document.getElementById('formRole').value,
            status: document.getElementById('formStatus').value,
            applied_date: document.getElementById('formDate').value,
            notes: document.getElementById('formNotes').value,
        };

        try {
            await api.createJob(data);
            authManager.showAlert('Job application added successfully!', 'success');
            await this.loadJobs();
        } catch (error) {
            authManager.showAlert('Failed to add job', 'error');
        }
    }

    showEditJobForm(jobId) {
        const job = this.jobs.find(j => j.id === jobId);
        if (!job) return;

        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = `
            <div class="card" style="max-width: 600px;">
                <h2 class="card-title">Edit Job Application</h2>
                <form id="editJobForm" onsubmit="dashboard.submitEditForm(event, ${jobId})">
                    <div class="form-group">
                        <label>Company *</label>
                        <input type="text" id="formCompany" value="${job.company}" required>
                    </div>
                    <div class="form-group">
                        <label>Role *</label>
                        <input type="text" id="formRole" value="${job.role}" required>
                    </div>
                    <div class="form-group">
                        <label>Status *</label>
                        <select id="formStatus" required>
                            <option value="applied" ${job.status === 'applied' ? 'selected' : ''}>Applied</option>
                            <option value="interview" ${job.status === 'interview' ? 'selected' : ''}>Interview</option>
                            <option value="offer" ${job.status === 'offer' ? 'selected' : ''}>Offer</option>
                            <option value="rejected" ${job.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Applied Date *</label>
                        <input type="date" id="formDate" value="${job.applied_date}" required>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="formNotes">${job.notes || ''}</textarea>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn btn-success">Update Job</button>
                        <button type="button" class="btn" style="background-color: #6c757d; color: white;" onclick="dashboard.renderDashboard()">Cancel</button>
                    </div>
                </form>
            </div>
        `;
    }

    async submitEditForm(e, jobId) {
        e.preventDefault();
        const data = {
            company: document.getElementById('formCompany').value,
            role: document.getElementById('formRole').value,
            status: document.getElementById('formStatus').value,
            applied_date: document.getElementById('formDate').value,
            notes: document.getElementById('formNotes').value,
        };

        try {
            await api.updateJob(jobId, data);
            authManager.showAlert('Job updated successfully!', 'success');
            await this.loadJobs();
        } catch (error) {
            authManager.showAlert('Failed to update job', 'error');
        }
    }

    async deleteJob(jobId) {
        if (!confirm('Are you sure you want to delete this job application?')) return;

        try {
            await api.deleteJob(jobId);
            authManager.showAlert('Job deleted successfully!', 'success');
            await this.loadJobs();
        } catch (error) {
            authManager.showAlert('Failed to delete job', 'error');
        }
    }

    async showHistory(jobId) {
        try {
            const history = await api.getStatusTimeline(jobId);
            const mainContent = document.getElementById('main-content');
            
            mainContent.innerHTML = `
                <div style="max-width: 800px;">
                    <button class="btn" style="background-color: #6c757d; color: white; margin-bottom: 2rem;" onclick="dashboard.renderDashboard()">← Back to Dashboard</button>
                    <div class="card">
                        <h2 class="card-title">${history.company} - Status Timeline</h2>
                        <div style="position: relative; padding: 20px;">
                            ${history.timeline.map(entry => `
                                <div style="display: flex; gap: 1rem; margin-bottom: 2rem; position: relative; padding-left: 30px;">
                                    <div style="position: absolute; left: 0; top: 5px; width: 16px; height: 16px; background-color: var(--primary-color); border-radius: 50%;"></div>
                                    <div>
                                        <strong>${entry.label}</strong>
                                        <p style="color: #666; margin-top: 0.5rem;">${new Date(entry.date).toLocaleString()}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            authManager.showAlert('Failed to load history', 'error');
        }
    }

    applyFilters() {
        const company = document.getElementById('searchCompany').value;
        const status = document.getElementById('statusFilter').value;

        const filters = {};
        if (company) filters.search = company;
        if (status) filters.status = status;

        this.loadJobs(filters);
    }
}

// Create global dashboard instance
const dashboard = new Dashboard();
