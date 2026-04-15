document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('botForm');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusBadge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');
    const consoleOutput = document.getElementById('consoleOutput');

    let pollInterval = null;
    let currentLogsCount = 0;

    function updateStatusUI(statusStr) {
        statusText.textContent = statusStr;
        
        // Reset classes
        statusBadge.classList.remove('running', 'stopping');
        
        if (statusStr === 'Running') {
            statusBadge.classList.add('running');
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else if (statusStr === 'Stopping...') {
            statusBadge.classList.add('stopping');
            startBtn.disabled = true;
            stopBtn.disabled = true;
        } else {
            // Offline
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    function appendLogs(logsArray) {
        if (logsArray.length === 0) return;
        
        // If we received more logs than we currently have, append the new ones
        if (logsArray.length > currentLogsCount) {
            const newLogs = logsArray.slice(currentLogsCount);
            
            newLogs.forEach(log => {
                const el = document.createElement('div');
                el.className = 'log-entry';
                el.textContent = log;
                consoleOutput.appendChild(el);
            });
            
            currentLogsCount = logsArray.length;
            // Scroll to bottom
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        } else if (logsArray.length < currentLogsCount) {
            // Server cleared logs (restarted)
            consoleOutput.innerHTML = '';
            currentLogsCount = 0;
            appendLogs(logsArray);
        }
    }

    function pollStatus() {
        fetch('/api/status')
            .then(res => res.json())
            .then(data => {
                updateStatusUI(data.status);
                appendLogs(data.logs);
                
                // Keep polling regardless of status so we can catch background stops
            })
            .catch(err => {
                console.error("Failed to poll status:", err);
                updateStatusUI("Disconnected from server");
            });
    }

    // Start polling immediately
    pollInterval = setInterval(pollStatus, 1500);
    pollStatus();

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const payload = {
            link: document.getElementById('meetLink').value,
            duration: document.getElementById('duration').value,
            profile: document.getElementById('profile').value
        };

        fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            if (data.error) {
                alert(data.error);
            }
        });
    });

    stopBtn.addEventListener('click', () => {
        fetch('/api/stop', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.error) {
                    alert(data.error);
                }
            });
    });
});
