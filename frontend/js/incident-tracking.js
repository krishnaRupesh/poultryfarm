async function loadIncidents() {
    clearStatus();
    const tbody = document.getElementById('incident-list');

    try {
        const incidents = await apiRequest('/api/incidents/');
        tbody.innerHTML = incidents.map((incident) => `
            <tr>
                <td>${incident.name}</td>
                <td>${incident.incident_type}</td>
                <td>${incident.incident_date}</td>
                <td>${incident.summary || ''}</td>
                <td>${money(incident.amount_spent)}</td>
                <td><button onclick="redirectToUpdate('${incident.incident_id}')">Update</button></td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

function redirectToUpdate(incidentId) {
    window.location.href = `incident-update.html?id=${incidentId}`;
}

document.addEventListener('DOMContentLoaded', loadIncidents);
