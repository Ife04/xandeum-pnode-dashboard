// API Configuration
const API_BASE = 'http://localhost:8000';
let performanceChart = null;
let allPnodes = [];
let currentPage = 1;
const itemsPerPage = 10;

// DOM Elements
const statsGrid = document.getElementById('statsGrid');
const tableBody = document.getElementById('tableBody');
const searchInput = document.getElementById('searchInput');
const activeOnlyToggle = document.getElementById('activeOnlyToggle');
const sortSelect = document.getElementById('sortSelect');
const refreshBtn = document.getElementById('refreshBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');
const nodeCount = document.getElementById('nodeCount');
const lastUpdate = document.getElementById('lastUpdate');
const statusList = document.getElementById('statusList');
const topPerformers = document.getElementById('topPerformers');

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    loadDashboardData();
    setupEventListeners();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Setup event listeners
function setupEventListeners() {
    refreshBtn.addEventListener('click', loadDashboardData);
    searchInput.addEventListener('input', filterAndRenderTable);
    activeOnlyToggle.addEventListener('change', filterAndRenderTable);
    sortSelect.addEventListener('change', filterAndRenderTable);
    prevBtn.addEventListener('click', goToPrevPage);
    nextBtn.addEventListener('click', goToNextPage);
    
    // Chart controls
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateChart(btn.dataset.chart);
        });
    });
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        showToast('Refreshing data...', 'info');
        await Promise.all([
            loadStats(),
            loadPnodes(),
            updateLastUpdate()
        ]);
        showToast('Data refreshed successfully!', 'success');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Failed to load data. Please try again.', 'error');
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/pnodes/stats/summary`);
        const data = await response.json();
        renderStats(data);
        renderStatusList(data);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load pNodes
async function loadPnodes() {
    try {
        const response = await fetch(`${API_BASE}/pnodes?limit=100`);
        const data = await response.json();
        allPnodes = data.pnodes || [];
        filterAndRenderTable();
        renderTopPerformers(allPnodes);
    } catch (error) {
        console.error('Error loading pnodes:', error);
    }
}

// Render statistics cards
function renderStats(stats) {
    const statCards = [
        {
            icon: 'fas fa-server',
            iconBg: '#667eea',
            value: stats.total_pnodes,
            label: 'Total pNodes',
            change: '+2 this week',
            changeType: 'positive'
        },
        {
            icon: 'fas fa-signal',
            iconBg: '#38a169',
            value: stats.active_pnodes,
            label: 'Active pNodes',
            change: `${((stats.active_pnodes / stats.total_pnodes) * 100).toFixed(1)}% uptime`,
            changeType: 'positive'
        },
        {
            icon: 'fas fa-coins',
            iconBg: '#d69e2e',
            value: `${(stats.total_stake / 1000000).toFixed(1)}M`,
            label: 'Total Stake',
            change: '+1.2%',
            changeType: 'positive'
        },
        {
            icon: 'fas fa-percentage',
            iconBg: '#e53e3e',
            value: `${stats.avg_commission.toFixed(2)}%`,
            label: 'Avg Commission',
            change: '-0.3%',
            changeType: 'positive'
        },
        {
            icon: 'fas fa-chart-line',
            iconBg: '#805ad5',
            value: `${(stats.avg_performance * 100).toFixed(1)}%`,
            label: 'Avg Performance',
            change: '+0.5%',
            changeType: 'positive'
        },
        {
            icon: 'fas fa-bolt',
            iconBg: '#3182ce',
            value: '142ms',
            label: 'Avg Response',
            change: '-12ms',
            changeType: 'positive'
        }
    ];

    statsGrid.innerHTML = statCards.map(card => `
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon" style="background: ${card.iconBg}">
                    <i class="${card.icon}"></i>
                </div>
            </div>
            <div class="stat-value">${card.value}</div>
            <div class="stat-label">${card.label}</div>
            <span class="stat-change ${card.changeType === 'positive' ? 'change-positive' : 'change-negative'}">
                ${card.change}
            </span>
        </div>
    `).join('');
}

// Render status list
function renderStatusList(stats) {
    const statusItems = [
        { label: 'Network Health', value: '98.5%', type: 'good' },
        { label: 'Avg Response Time', value: '142ms' },
        { label: 'Uptime (24h)', value: '99.8%', type: 'good' },
        { label: 'Active pNodes', value: `${stats.active_pnodes}/${stats.total_pnodes}`, type: 'good' },
        { label: 'Failed Votes', value: '0.2%', type: 'warning' }
    ];

    statusList.innerHTML = statusItems.map(item => `
        <div class="status-item">
            <span class="status-label">${item.label}</span>
            <span class="status-value ${item.type === 'good' ? 'status-good' : item.type === 'warning' ? 'status-warning' : ''}">
                ${item.value}
            </span>
        </div>
    `).join('');
}

// Render top performers
function renderTopPerformers(pnodes) {
    const topPerformers = [...pnodes]
        .sort((a, b) => b.performance_score - a.performance_score)
        .slice(0, 5);

    const performersHTML = topPerformers.map((pnode, index) => `
        <div class="performer">
            <div class="performer-rank">${index + 1}</div>
            <div class="performer-info">
                <div class="performer-id">${pnode.pubkey.substring(0, 16)}...</div>
                <div class="performer-stats">
                    ${pnode.ip} • ${pnode.commission.toFixed(2)}% commission
                </div>
            </div>
            <div class="performer-score">${(pnode.performance_score * 100).toFixed(1)}%</div>
        </div>
    `).join('');

    document.getElementById('topPerformers').innerHTML = performersHTML;
}

// Filter and render table
function filterAndRenderTable() {
    const searchTerm = searchInput.value.toLowerCase();
    const activeOnly = activeOnlyToggle.checked;
    const sortBy = sortSelect.value;

    let filtered = allPnodes.filter(pnode => {
        const matchesSearch = 
            pnode.pubkey.toLowerCase().includes(searchTerm) ||
            pnode.ip.toLowerCase().includes(searchTerm) ||
            pnode.data_center?.toLowerCase().includes(searchTerm);
        
        const matchesActive = !activeOnly || pnode.is_active;
        
        return matchesSearch && matchesActive;
    });

    // Sort
    filtered.sort((a, b) => {
        switch (sortBy) {
            case 'stake':
                return b.stake - a.stake;
            case 'performance':
                return b.performance_score - a.performance_score;
            case 'commission':
                return a.commission - b.commission;
            case 'status':
                return (b.is_active ? 1 : 0) - (a.is_active ? 1 : 0);
            default:
                return 0;
        }
    });

    renderTable(filtered);
}

// Render table with pagination
function renderTable(pnodes){
    const totalPages = Math.ceil(pnodes.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = pnodes.slice(startIndex, endIndex);

    // Update pagination controls
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    nodeCount.textContent = `Showing ${pageData.length} of ${pnodes.length} pNodes`;

    // Render table rows
    tableBody.innerHTML = pageData.map(pnode => `
        <tr>
            <td>
                <span class="status-badge ${pnode.is_active ? 'status-active' : 'status-inactive'}">
                    ${pnode.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div style="font-family: monospace; font-size: 12px;">
                    ${pnode.pubkey.substring(0, 16)}...
                </div>
                <div style="font-size: 11px; color: #718096;">v${pnode.version}</div>
            </td>
            <td>
                <div>${pnode.ip}</div>
                <div style="font-size: 12px; color: #718096;">${pnode.data_center || 'Unknown'}</div>
            </td>
            <td>
                <strong>${formatStake(pnode.stake)}</strong>
            </td>

        </tr>`).join('');

}



    
            