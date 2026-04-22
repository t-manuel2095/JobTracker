/**
 * API.js - Handles all API communication with the Django backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    constructor() {
        this.token = this.getToken();
    }

    getToken() {
        return localStorage.getItem('auth_token');
    }

    setToken(token) {
        localStorage.setItem('auth_token', token);
        this.token = token;
    }

    removeToken() {
        localStorage.removeItem('auth_token');
        this.token = null;
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(),
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.removeToken();
                    window.location.href = 'index.html';
                }
                console.error('API Error Response:', data);
                throw new Error(`API Error: ${response.statusText}`);
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // ===== AUTH ENDPOINTS =====

    async register(username, email, password) {
        return this.request('/auth/users/', {
            method: 'POST',
            body: JSON.stringify({ username, email, password }),
        });
    }

    async login(username, password) {
        return fetch('http://localhost:8000/auth/jwt/create/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        }).then(r => r.json());
    }

    async logout() {
        this.removeToken();
    }

    // ===== JOB APPLICATION ENDPOINTS =====

    async getJobs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/jobs/?${query}`);
    }

    async getJob(jobId) {
        return this.request(`/jobs/${jobId}/`);
    }

    async createJob(data) {
        return this.request('/jobs/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateJob(jobId, data) {
        return this.request(`/jobs/${jobId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async deleteJob(jobId) {
        return this.request(`/jobs/${jobId}/`, {
            method: 'DELETE',
        });
    }

    // ===== STATUS HISTORY ENDPOINTS =====

    async getJobHistory(jobId) {
        return this.request(`/jobs/${jobId}/history/`);
    }

    async getStatusTimeline(jobId) {
        return this.request(`/jobs/${jobId}/status_timeline/`);
    }

    // ===== ANALYTICS ENDPOINTS =====

    async getStats() {
        return this.request('/stats/stats/');
    }

    async getDetailedStats() {
        return this.request('/stats/detailed_stats/');
    }
}

// Create global API client instance
const api = new APIClient();
