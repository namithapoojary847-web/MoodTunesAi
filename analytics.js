/**
 * MoodTunes - Analytics Dashboard & Chart.js Visualizations
 */

let moodPieChart = null;
let trendLineChart = null;

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('moodPieChartCanvas')) {
        initAnalyticsDashboard();
    }
});

async function initAnalyticsDashboard() {
    try {
        const response = await fetch('/api/analytics/summary');
        const data = await response.json();

        if (data.success) {
            updateAnalyticsSummaryCards(data);
            renderMoodPieChart(data.distribution);
            renderWeeklyTrendChart(data.weekly_trend);
            renderRecentHistoryTable(data.recent_history);
        }
    } catch (err) {
        console.error("Error loading analytics data:", err);
    }
}

function updateAnalyticsSummaryCards(data) {
    const totalDetections = document.getElementById('totalDetectionsCount');
    const dominantMood = document.getElementById('dominantMoodLabel');

    if (totalDetections) totalDetections.textContent = data.total_detections || 0;
    if (dominantMood) dominantMood.textContent = data.dominant_mood || 'Neutral';
}

function renderMoodPieChart(distribution) {
    const ctx = document.getElementById('moodPieChartCanvas').getContext('2d');
    if (moodPieChart) moodPieChart.destroy();

    const labels = Object.keys(distribution);
    const values = Object.values(distribution);
    const colors = ['#ffb703', '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899', '#10b981'];

    moodPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#131927'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { family: 'Outfit', size: 12 } }
                }
            }
        }
    });
}

function renderWeeklyTrendChart(weeklyTrend) {
    const ctx = document.getElementById('weeklyTrendChartCanvas').getContext('2d');
    if (trendLineChart) trendLineChart.destroy();

    trendLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeklyTrend.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Emotion Detections',
                data: weeklyTrend.counts || [2, 4, 3, 7, 5, 8, 6],
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124, 58, 237, 0.15)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderRecentHistoryTable(logs) {
    const tableBody = document.getElementById('recentHistoryTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    if (!logs || logs.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:1.5rem; color:#64748b;">No emotion logs recorded yet. Start camera scan to log your mood!</td></tr>';
        return;
    }

    logs.forEach(log => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="padding: 0.75rem 1rem;">${log.emotion}</td>
            <td style="padding: 0.75rem 1rem;"><span style="color: #10b981;">${log.confidence}%</span></td>
            <td style="padding: 0.75rem 1rem; color: #94a3b8;">${new Date(log.created_at).toLocaleString()}</td>
        `;
        tableBody.appendChild(tr);
    });
}
