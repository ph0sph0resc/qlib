/**
 * Main JavaScript for QLib Web
 */

/**
 * API helper functions
 */
const API = {
    baseUrl: '/api',

    async get(endpoint, params = {}) {
        let url = this.baseUrl + endpoint;
        if (Object.keys(params).length > 0) {
            const queryString = new URLSearchParams(params).toString();
            url += '?' + queryString;
        }
        const response = await fetch(url);
        return await response.json();
    },

    async post(endpoint, data = {}) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    },

    async delete(endpoint) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'DELETE'
        });
        return await response.json();
    }
};

/**
 * Status badge helper
 */
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge bg-secondary">等待中</span>',
        'running': '<span class="badge bg-primary">运行中</span>',
        'completed': '<span class="badge bg-success">已完成</span>',
        'failed': '<span class="badge bg-danger">失败</span>',
        'cancelled': '<span class="badge bg-warning">取消</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">未知</span>';
}

/**
 * Get task type label
 */
function getTaskTypeLabel(taskType) {
    const labels = {
        'factor_test': '因子测试',
        'model_train': '模型训练',
        'backtest': '回测'
    };
    return labels[taskType] || taskType;
}

/**
 * Format date
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

/**
 * Load recent tasks for dashboard
 */
async function loadRecentTasks() {
    try {
        const result = await API.get('/tasks');
        if (result.success) {
            displayRecentTasks(result.tasks.slice(0, 10));
        }
    } catch (error) {
        console.error('Failed to load recent tasks:', error);
    }
}

/**
 * Display recent tasks in table
 */
function displayRecentTasks(tasks) {
    const tbody = document.querySelector('#recent-tasks-table tbody');
    if (!tbody) return;

    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">暂无任务</td></tr>';
        return;
    }

    tbody.innerHTML = tasks.map(task => `
        <tr>
            <td><code>${task.id.substring(0, 8)}</code></td>
            <td>Unnamed Task</td>
            <td>${getTaskTypeLabel(task.type)}</td>
            <td>${getStatusBadge(task.status)}</td>
            <td>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" style="width: ${task.progress}%">
                        ${task.progress.toFixed(0)}%
                    </div>
                </div>
            </td>
            <td>${formatDate(task.created_at)}</td>
        </tr>
    `).join('');
}

/**
 * Update system status
 */
async function updateSystemStatus() {
    try {
        const result = await API.get('/status');
        if (result.status === 'ok') {
            const statusBadge = document.getElementById('system-status');
            if (statusBadge) {
                const runningCount = result.tasks_running || 0;
                if (runningCount > 0) {
                    statusBadge.className = 'badge bg-success';
                    statusBadge.textContent = `运行中 (${runningCount})`;
                } else {
                    statusBadge.className = 'badge bg-secondary';
                    statusBadge.textContent = '空闲';
                }
            }
        }
    } catch (error) {
        console.error('Failed to update system status:', error);
    }
}

// Auto-update system status every 30 seconds
setInterval(updateSystemStatus, 30000);

// Initial status update
document.addEventListener('DOMContentLoaded', function() {
    updateSystemStatus();
});

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 200);
    }, 5000);
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('已复制到剪贴板', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showAlert('复制失败', 'danger');
    });
}

/**
 * Download file
 */
function downloadFile(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Format number
 */
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return num.toFixed(decimals);
}

/**
 * Format percentage
 */
function formatPercentage(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return (num * 100).toFixed(decimals) + '%';
}

/**
 * Format large number
 */
function formatLargeNumber(num) {
    if (num === null || num === undefined) return '-';
    if (num >= 100000000) {
        return (num / 100000000).toFixed(2) + '亿';
    } else if (num >= 10000) {
        return (num / 10000).toFixed(2) + '万';
    }
    return num.toLocaleString();
}
