async function loadData() {
    try {
        // Fetch stats
        const statsRes = await fetch('/api/stats');
        const stats = await statsRes.json();
        document.getElementById('user-count').textContent = stats.users;

        // Fetch configs
        const configRes = await fetch('/api/config');
        const configData = await configRes.json();
        const configs = configData.configs;

        if (configs['SYSTEM_PROMPT']) {
            document.getElementById('SYSTEM_PROMPT').value = configs['SYSTEM_PROMPT'];
        }
        if (configs['FUGLE_API_KEY']) {
            document.getElementById('FUGLE_API_KEY').value = configs['FUGLE_API_KEY'];
        }
        if (configs['POLYGON_API_KEY']) {
            document.getElementById('POLYGON_API_KEY').value = configs['POLYGON_API_KEY'];
        }
    } catch (e) {
        console.error("Failed to load initial data:", e);
    }
}

async function saveConfig(keyName) {
    const value = document.getElementById(keyName).value;
    const btn = event.target;
    const originalText = btn.textContent;
    
    btn.textContent = 'Saving...';
    btn.style.opacity = '0.7';

    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key_name: keyName, value: value })
        });
        
        if (res.ok) {
            btn.textContent = 'Saved! ✓';
            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
                btn.style.opacity = '1';
            }, 2000);
        } else {
            alert('Failed to save config.');
            btn.textContent = originalText;
            btn.style.opacity = '1';
        }
    } catch (e) {
        console.error(e);
        alert('Network error during save.');
        btn.textContent = originalText;
        btn.style.opacity = '1';
    }
}

// Ensure init on load
window.addEventListener('DOMContentLoaded', loadData);
