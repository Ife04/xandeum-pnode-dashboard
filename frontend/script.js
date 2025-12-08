// ============================================
// Xandeum pNode Dashboard - Main Script
// ============================================

// Configuration
const API_BASE = 'http://localhost:8000';
let allPnodes = [];
let currentNetwork = 'testnet';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
});

function initializeDashboard() {
    setupEventListeners();
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
}

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.querySelector('.btn-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboardData);
    }
    
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }
    
    // Active only toggle
    const activeOnly = document.getElementById('activeOnly');
    if (activeOnly) {
        activeOnly.addEventListener('change', filterTable);
    }
    
    // Sort select
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', filterTable);
    }
}

// Network switching
async function switchNetwork() {
    const select = document.getElementById('networkSelect');
    currentNetwork = select.value;
    
    const networkStatus = document.getElementById('networkStatus');
    const statusIcon = document.querySelector('#dataSourceInfo i');
    
    switch(currentNetwork) {
        case 'testnet':
            networkStatus.textContent = 'Connected to Xandeum Testnet';
            statusIcon.style.color = '#38a169';
            break;
        case 'mainnet':
            networkStatus.textContent = 'Connected to Xandeum Mainnet';
            statusIcon.style.color = '#667eea';
            break;
        case 'demo':
            networkStatus.textContent = 'Using Demo Data';
            statusIcon.style.color = '#d69e2e';
            break;
    }
    
    showNotification(`Switching to ${currentNetwork}...`, 'info');
    await loadDashboardData();
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        showNotification(`Loading ${currentNetwork} data...`, 'info');
        
        // Load stats summary
        const statsResponse = await fetch(`${API_BASE}/pnodes/stats/summary?network=${currentNetwork}`);
        const stats = await statsResponse.json();
        renderStats(stats);
        
        // Load pnodes
        const pnodesResponse = await fetch(`${API_BASE}/pnodes?network=${currentNetwork}&limit=100`);
        const pnodesData = await pnodesResponse.json();
        allPnodes = pnodesData.pnodes || [];
        filterTable();
        
        // Load network info
        await loadNetworkInfo();
        
        // Update timestamp
        const now = new Date();
        document.getElementById('lastUpdateTime').textContent = now.toLocaleTimeString();
        
        showNotification(`${currentNetwork.charAt(0).toUpperCase() + currentNetwork.slice(1)} data loaded successfully!`, 'success');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification(`Failed to load ${currentNetwork} data. Check if backend is running.`, 'error');
        
        // If testnet/mainnet fails, switch to demo
        if (currentNetwork !== 'demo') {
            showNotification('Falling back to demo data...', 'warning');
            document.getElementById('networkSelect').value = 'demo';
            switchNetwork();
        }
    }
}

// Load network information
async function loadNetworkInfo() {
    try {
        const response = await fetch(`${API_BASE}/pnodes/network/info?network=${currentNetwork}`);
        const data = await response.json();
        
        document.getElementById('currentEpoch').textContent = data.epoch || 0;
        document.getElementById('currentSlot').textContent = data.slot || 0;
    } catch (error) {
        console.error('Error loading network info:', error);
        document.getElementById('currentEpoch').textContent = '0';
        document.getElementById('currentSlot').textContent = '0';
    }
}

// Render statistics
function renderStats(stats) {
    const statsGrid = document.getElementById('statsGrid');
    if (!statsGrid) return;
    
    const statCards = [
        {
            icon: 'fas fa-server',
            iconColor: '#667eea',
            value: stats.total_pnodes || 0,
            label: 'Total pNodes',
            change: '+2 this week',
            changeType: 'up'
        },
        {
            icon: 'fas fa-signal',
            iconColor: '#38a169',
            value: stats.active_pnodes || 0,
            label: 'Active pNodes',
            change: stats.total_pnodes ? `${((stats.active_pnodes / stats.total_pnodes) * 100).toFixed(1)}% uptime` : '100% uptime',
            changeType: 'up'
        },
        {
            icon: 'fas fa-coins',
            iconColor: '#d69e2e',
            value: stats.total_stake ? `${(stats.total_stake / 1000000).toFixed(1)}M` : '0',
            label: 'Total Stake',
            change: '+1.2%',
            changeType: 'up'
        },
        {
            icon: 'fas fa-percentage',
            iconColor: '#e53e3e',
            value: stats.avg_commission ? `${stats.avg_commission.toFixed(2)}%` : '0%',
            label: 'Avg Commission',
            change: '-0.3%',
            changeType: 'down'
        },
        {
            icon: 'fas fa-chart-line',
            iconColor: '#805ad5',
            value: stats.avg_performance ? `${(stats.avg_performance * 100).toFixed(1)}%` : '0%',
            label: 'Avg Performance',
            change: '+0.5%',
            changeType: 'up'
        }
    ];

    statsGrid.innerHTML = statCards.map(card => `
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon" style="background: ${card.iconColor}">
                    <i class="${card.icon}"></i>
                </div>
            </div>
            <div class="stat-value">${card.value}</div>
            <div class="stat-label">${card.label}</div>
            <span class="stat-change change-${card.changeType}">
                ${card.change}
            </span>
        </div>
    `).join('');
}

// Filter and render table
function filterTable() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const activeOnly = document.getElementById('activeOnly')?.checked || false;
    const sortBy = document.getElementById('sortSelect')?.value || 'stake';

    let filtered = allPnodes.filter(pnode => {
        const matchesSearch = 
            pnode.pubkey.toLowerCase().includes(searchTerm) ||
            pnode.ip.toLowerCase().includes(searchTerm) ||
            (pnode.data_center && pnode.data_center.toLowerCase().includes(searchTerm));
        
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
            default:
                return 0;
        }
    });

    renderTable(filtered);
}

// Render table
function renderTable(pnodes) {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;
    
    if (pnodes.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-search" style="font-size: 48px; margin-bottom: 20px; display: block;"></i>
                    No pNodes found matching your criteria
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = pnodes.map(pnode => {
        const performancePercent = Math.round((pnode.performance_score || 0) * 100);
        let barClass = 'bar-high';
        if (performancePercent < 70) barClass = 'bar-low';
        else if (performancePercent < 90) barClass = 'bar-medium';

        const stakeFormatted = formatStake(pnode.stake || 0);

        return `
            <tr>
                <td>
                    <span class="status-badge ${pnode.is_active ? 'status-active' : 'status-inactive'}">
                        ${pnode.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <div style="font-family: monospace; font-size: 12px; font-weight: 500;">
                        ${(pnode.pubkey || '').substring(0, 16)}...
                    </div>
                </td>
                <td>${pnode.ip || 'Unknown'}</td>
                <td><strong>${stakeFormatted}</strong></td>
                <td>${(pnode.commission || 0).toFixed(2)}%</td>
                <td>
                    <div class="performance-bar">
                        <div class="bar-container">
                            <div class="bar-fill ${barClass}" style="width: ${performancePercent}%"></div>
                        </div>
                        <span>${performancePercent}%</span>
                    </div>
                </td>
                <td>v${pnode.version || '1.0.0'}</td>
                <td>${formatTime(pnode.last_seen)}</td>
            </tr>
        `;
    }).join('');
}

// Utility functions
function formatStake(stake) {
    if (stake >= 1000000) return `${(stake / 1000000).toFixed(2)}M`;
    if (stake >= 1000) return `${(stake / 1000).toFixed(1)}K`;
    return stake;
}

function formatTime(isoString) {
    try {
        if (!isoString) return 'Just now';
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
        return 'Just now';
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;margin-left:10px;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Clear previous notifications
    container.innerHTML = '';
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement === container) {
            notification.remove();
        }
    }, 5000);
}

// Initialize on load
window.onload = initializeDashboard;
// Modal functions
function showApiInfo() {
    document.getElementById('apiInfoModal').style.display = 'flex';
}

function closeApiInfo() {
    document.getElementById('apiInfoModal').style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('apiInfoModal');
    if (event.target === modal) {
        closeApiInfo();
    }
});
