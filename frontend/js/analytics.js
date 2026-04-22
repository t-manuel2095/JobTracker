/**
 * ANALYTICS.js - Handles analytics dashboard
 */

class Analytics {
    async renderAnalytics() {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = '<p style="text-align: center;">Loading analytics...</p>';

        try {
            const stats = await api.getStats();
            
            mainContent.innerHTML = `
                <button class="btn" style="background-color: #6c757d; color: white; margin-bottom: 2rem;" onclick="dashboard.renderDashboard()">← Back to Dashboard</button>
                
                <h2 style="margin-bottom: 2rem;">📈 Analytics Dashboard</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <p>Total Applications</p>
                        <h3>${stats.total_applications}</h3>
                    </div>
                    <div class="stat-card">
                        <p>Success Rate</p>
                        <h3>${stats.success_rate_percentage}%</h3>
                    </div>
                    <div class="stat-card">
                        <p>Rejection Rate</p>
                        <h3>${stats.rejection_rate_percentage}%</h3>
                    </div>
                </div>

                <div class="card">
                    <h3>Status Breakdown</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 4px;">
                            <p style="margin: 0; color: #666;">Applied</p>
                            <h4 style="margin: 0.5rem 0; color: var(--primary-color);">${stats.status_breakdown.applied} (${stats.status_percentages.applied}%)</h4>
                        </div>
                        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 4px;">
                            <p style="margin: 0; color: #666;">Interview</p>
                            <h4 style="margin: 0.5rem 0; color: var(--warning-color);">${stats.status_breakdown.interview} (${stats.status_percentages.interview}%)</h4>
                        </div>
                        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 4px;">
                            <p style="margin: 0; color: #666;">Offer</p>
                            <h4 style="margin: 0.5rem 0; color: var(--success-color);">${stats.status_breakdown.offer} (${stats.status_percentages.offer}%)</h4>
                        </div>
                        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 4px;">
                            <p style="margin: 0; color: #666;">Rejected</p>
                            <h4 style="margin: 0.5rem 0; color: var(--danger-color);">${stats.status_breakdown.rejected} (${stats.status_percentages.rejected}%)</h4>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            mainContent.innerHTML = '<p style="text-align: center; color: var(--danger-color);">Failed to load analytics</p>';
        }
    }
}

// Create global analytics instance
const analytics = new Analytics();
