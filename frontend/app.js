// Chart Setup
const ctx = document.getElementById('liveChart').getContext('2d');
const liveChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Pressure (PSI)',
                data: [],
                borderColor: '#00d2ff',
                backgroundColor: 'rgba(0, 210, 255, 0.1)',
                fill: true,
                tension: 0.4,
                yAxisID: 'y',
            },
            {
                label: 'Flow Rate Up (bbl/m)',
                data: [],
                borderColor: '#00ff88',
                tension: 0.4,
                yAxisID: 'y1',
            }
        ]
    },
    options: {
        responsive: true,
        animation: { duration: 0 },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: '#a4b0be' }
            },
            y: {
                position: 'left',
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: '#a4b0be' }
            },
            y1: {
                position: 'right',
                grid: { display: false },
                ticks: { color: '#a4b0be' }
            }
        },
        plugins: {
            legend: {
                display: true,
                labels: { color: '#f5f6fa' }
            }
        }
    }
});

// State Management
let currentRole = 'operator';
const roleSelect = document.getElementById('roleSelect');
const statusIndicator = document.getElementById('systemStatus');
const statusText = statusIndicator.querySelector('.status-text');

// WebSocket Connection
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    updateDashboard(message);
};

ws.onclose = () => {
    console.log('WS connection closed. Reconnecting...');
    setTimeout(() => location.reload(), 5000);
};

function updateDashboard(payload) {
    const { data, alerts, status } = payload;

    // Update Stats
    document.getElementById('pressureVal').innerText = data.pressure;
    document.getElementById('flowUpVal').innerText = data.flow_rate_upstream;
    document.getElementById('flowDownVal').innerText = data.flow_rate_downstream;
    document.getElementById('tempVal').innerText = data.temperature;

    // Update System Status
    if (status === 'Risk' || alerts.length > 0) {
        statusIndicator.classList.add('risk');
        statusText.innerText = 'Risk Detected';
    } else {
        statusIndicator.classList.remove('risk');
        statusText.innerText = 'System Normal';
    }

    // Update Chart
    const timeLabel = new Date(data.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    liveChart.data.labels.push(timeLabel);
    liveChart.data.datasets[0].data.push(data.pressure);
    liveChart.data.datasets[1].data.push(data.flow_rate_upstream);

    if (liveChart.data.labels.length > 20) {
        liveChart.data.labels.shift();
        liveChart.data.datasets[0].data.shift();
        liveChart.data.datasets[1].data.shift();
    }
    liveChart.update();

    // Update Alerts List
    updateAlerts(alerts);
}

function updateAlerts(alerts) {
    const alertList = document.getElementById('alertList');
    const alertCount = document.getElementById('alertCount');
    
    alertCount.innerText = alerts.length;
    
    if (alerts.length === 0) {
        alertList.innerHTML = '<div class="empty-state">No critical issues detected.</div>';
        return;
    }

    alertList.innerHTML = alerts.reverse().map(alert => `
        <div class="alert-item ${alert.severity === 'Critical' ? 'critical' : ''}">
            <h4>${alert.type} - ${alert.zone}</h4>
            <p>${alert.message}</p>
            <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
        </div>
    `).join('');
}

// Role Based Logic
roleSelect.addEventListener('change', (e) => {
    currentRole = e.target.value;
    document.body.className = `dark-mode role-${currentRole}`;
    
    // Toggle visibility based on role
    const executiveControls = document.querySelector('.simulation-controls');
    if (currentRole === 'executive' || currentRole === 'operator') {
        executiveControls.classList.remove('hidden');
    } else {
        executiveControls.classList.add('hidden');
    }
});

// Simulation Controls
async function triggerSimulation(type, active) {
    try {
        const resp = await fetch(`http://localhost:8000/trigger/${type}?active=${active}`, {
            method: 'POST'
        });
        const result = await resp.json();
        console.log(result.message);
    } catch (e) {
        console.error('Failed to trigger simulation:', e);
    }
}

document.getElementById('leakBtn').addEventListener('click', () => {
    triggerSimulation('leak', true);
    setTimeout(() => triggerSimulation('leak', false), 5000); // Auto reset after 5s for demo
});

document.getElementById('theftBtn').addEventListener('click', () => {
    triggerSimulation('theft', true);
    setTimeout(() => triggerSimulation('theft', false), 5000);
});

document.getElementById('resetBtn').addEventListener('click', () => {
    triggerSimulation('leak', false);
    triggerSimulation('theft', false);
});

// Modal Logic
const reportOverlay = document.getElementById('reportOverlay');
const openReportBtn = document.getElementById('openReportBtn');
const closeReportBtn = document.getElementById('closeReportBtn');
const submitReportBtn = document.getElementById('submitReport');

openReportBtn.addEventListener('click', () => {
    reportOverlay.classList.remove('hidden');
});

closeReportBtn.addEventListener('click', () => {
    reportOverlay.classList.add('hidden');
});

submitReportBtn.addEventListener('click', async () => {
    const message = document.getElementById('reportMsg').value;
    const zone = document.getElementById('reportZone').value;

    if (!message) return alert('Please describe the issue.');

    try {
        const resp = await fetch('http://localhost:8000/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, zone })
        });
        
        if (resp.ok) {
            alert('Report submitted successfully!');
            reportOverlay.classList.add('hidden');
            document.getElementById('reportMsg').value = '';
            document.getElementById('reportZone').value = '';
        }
    } catch (e) {
        console.error('Failed to submit report:', e);
    }
});
