/**
 * AquaTrace Dashboard - Real-time Monitoring
 * Handles data fetching, chart updates, and parameter monitoring
 */

// =====================
// Configuration
// =====================
const MAX_DATA_POINTS = 20;  // Maximum number of points to display on charts
const FETCH_INTERVAL = 3000; // Fetch data every 3 seconds
let farmId = null;  // Set from template
let fetchTimer = null;

// =====================
// Data Storage
// =====================
const history = {
  labels: [],
  temperature: [],
  oxygen: [],
  ph: [],
  ammonia: []
};

// =====================
// DOM Elements
// =====================
const elements = {
  tempValue: document.getElementById('temperature-value'),
  oxygenValue: document.getElementById('oxygen-value'),
  phValue: document.getElementById('ph-value'),
  ammoniaValue: document.getElementById('ammonia-value'),
  lastUpdate: document.getElementById('last-update'),
  tempBadge: document.getElementById('temp-badge'),
  oxyBadge: document.getElementById('oxy-badge'),
  phBadge: document.getElementById('ph-badge'),
  ammoBadge: document.getElementById('ammo-badge'),
  loading: document.getElementById('loading-indicator')
};

// =====================
// Utility Functions
// =====================

/**
 * Determine badge status based on value and thresholds
 */
function getBadgeStatus(value, min, max) {
  if (value < min || value > max) {
    return { text: "Danger", class: "danger" };
  } else if (Math.abs(value - min) < 1 || Math.abs(value - max) < 1) {
    return { text: "Warning", class: "warning" };
  } else {
    return { text: "Normal", class: "normal" };
  }
}

/**
 * Update parameter badge
 */
function updateBadge(badge, value, min, max) {
  const status = getBadgeStatus(value, min, max);
  badge.textContent = status.text;
  badge.className = `parameter-badge ${status.class}`;
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
  if (!timestamp) return '--';
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  } catch (e) {
    return timestamp;
  }
}

/**
 * Show error notification
 */
function showError(message) {
  console.error(message);
  
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.innerHTML = `
    <i class="fas fa-exclamation-circle"></i>
    <span>${message}</span>
  `;
  document.body.appendChild(toast);
  
  // Remove after 5 seconds
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

/**
 * Show loading indicator
 */
function showLoading(show) {
  if (elements.loading) {
    elements.loading.style.display = show ? 'flex' : 'none';
  }
}

// =====================
// Data Fetching
// =====================

/**
 * Fetch sensor data from API
 */
async function fetchData() {
  if (!farmId) {
    console.error('Farm ID not set');
    return;
  }

  try {
    showLoading(true);
    
    const response = await fetch(`/api/data/${farmId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.error || 'Unknown error');
    }

    const data = result.data;
    updateDashboard(data);

  } catch (error) {
    console.error('Fetch error:', error);
    showError('Failed to load data. Retrying...');
  } finally {
    showLoading(false);
  }
}

/**
 * Update dashboard with new data
 */
function updateDashboard(data) {
  // Update parameter values
  elements.tempValue.textContent = `${data.temperature} °C`;
  elements.oxygenValue.textContent = `${data.oxygen} mg/L`;
  elements.phValue.textContent = data.ph;
  elements.ammoniaValue.textContent = `${data.ammonia} mg/L`;
  elements.lastUpdate.textContent = formatTimestamp(data.timestamp);

  // Update badges with thresholds
  const thresholds = data.thresholds || {};
  updateBadge(elements.tempBadge, data.temperature, 
              thresholds.temp_min || 23, thresholds.temp_max || 26);
  updateBadge(elements.oxyBadge, data.oxygen, 
              thresholds.oxygen_min || 5, 10);
  updateBadge(elements.phBadge, data.ph, 7, 7.5);
  updateBadge(elements.ammoBadge, data.ammonia, 0, 
              thresholds.ammonia_max || 0.1);

  // Add to history
  const timeLabel = new Date().toLocaleTimeString();
  history.labels.push(timeLabel);
  history.temperature.push(data.temperature);
  history.oxygen.push(data.oxygen);
  history.ph.push(data.ph);
  history.ammonia.push(data.ammonia);

  // Limit history size
  if (history.labels.length > MAX_DATA_POINTS) {
    Object.keys(history).forEach(key => history[key].shift());
  }

  // Update charts
  updateCharts();

  // Show alert if risk is high
  if (data.alert) {
    showAlert(data.risk);
  }
}

/**
 * Show risk alert
 */
function showAlert(riskMessage) {
  const alert = document.createElement('div');
  alert.className = 'risk-alert';
  alert.innerHTML = `
    <i class="fas fa-exclamation-triangle"></i>
    <strong>Alert:</strong> ${riskMessage}
  `;
  
  const container = document.querySelector('.dashboard-wrapper');
  if (container && !document.querySelector('.risk-alert')) {
    container.insertBefore(alert, container.firstChild);
    
    // Remove after 10 seconds
    setTimeout(() => {
      alert.classList.add('fade-out');
      setTimeout(() => alert.remove(), 300);
    }, 10000);
  }
}

// =====================
// Chart Management
// =====================

let charts = {};

/**
 * Create a line chart
 */
function createChart(canvasId, dataKey, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) {
    console.error(`Canvas ${canvasId} not found`);
    return null;
  }

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: history.labels,
      datasets: [{
        data: history[dataKey],
        borderColor: color,
        backgroundColor: color + '20',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: { display: false },
        y: { 
          display: true,
          grid: {
            color: 'rgba(0,0,0,0.05)'
          },
          ticks: {
            font: { size: 10 }
          }
        }
      },
      animation: {
        duration: 300
      }
    }
  });
}

/**
 * Initialize all charts
 */
function initializeCharts() {
  charts.temperature = createChart('tempChart', 'temperature', '#e53935');
  charts.oxygen = createChart('oxyChart', 'oxygen', '#1e88e5');
  charts.ph = createChart('phChart', 'ph', '#43a047');
  charts.ammonia = createChart('ammoChart', 'ammonia', '#ffb300');
}

/**
 * Update all charts with new data
 */
function updateCharts() {
  Object.values(charts).forEach(chart => {
    if (chart) {
      chart.update('none'); // Update without animation for smooth transitions
    }
  });
}

// =====================
// Control Functions
// =====================

/**
 * Manual refresh button handler
 */
function refreshData() {
  fetchData();
  
  // Visual feedback
  const btn = event.target.closest('button');
  if (btn) {
    const icon = btn.querySelector('i');
    icon.classList.add('fa-spin');
    setTimeout(() => icon.classList.remove('fa-spin'), 1000);
  }
}

/**
 * Start automatic data fetching
 */
function startAutoFetch() {
  if (fetchTimer) {
    clearInterval(fetchTimer);
  }
  fetchTimer = setInterval(fetchData, FETCH_INTERVAL);
}

/**
 * Stop automatic data fetching
 */
function stopAutoFetch() {
  if (fetchTimer) {
    clearInterval(fetchTimer);
    fetchTimer = null;
  }
}

// =====================
// Initialization
// =====================

/**
 * Initialize dashboard
 */
function initializeDashboard() {
  // Get farm ID from page
  const farmIdElement = document.getElementById('farm-id');
  if (farmIdElement) {
    farmId = farmIdElement.value;
  } else {
    console.error('Farm ID not found on page');
    showError('Configuration error: Farm ID missing');
    return;
  }

  // Initialize charts
  initializeCharts();

  // Fetch initial data
  fetchData();

  // Start auto-refresh
  startAutoFetch();

  // Stop fetching when page is hidden
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stopAutoFetch();
    } else {
      startAutoFetch();
    }
  });

  console.log('Dashboard initialized for farm ID:', farmId);
}

// =====================
// Page Load
// =====================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
  initializeDashboard();
}

// Cleanup on page unload
window.addEventListener('beforeunload', stopAutoFetch);

// Export functions for use in HTML
window.refreshData = refreshData;