// Function to load incidents
function loadIncidents() {
    const incidents = getIncidents();
    const tbody = document.getElementById('incident-list');
    tbody.innerHTML = ''; // Clear previous rows

    incidents.forEach(incident => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${incident.name}</td>
            <td>${incident.type}</td>
            <td>${incident.date}</td>
            <td>${incident.summary}</td>
            <td>${incident.amountSpent}</td>
            <td><button onclick="redirectToUpdate('${incident.id}')">Update</button></td>
        `;
        tbody.appendChild(row);
    });
}

// Function to simulate fetching incidents from backend
function getIncidents() {
    return [
        { id: 'INC001', name: 'Electric Issue', type: 'electric', date: '2024-09-01', summary: 'Power outage', amountSpent: '100' },
        { id: 'INC002', name: 'Hens Feed', type: 'hens', date: '2024-09-02', summary: 'Purchased feed', amountSpent: '200' },
    ].sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by incident date descending
}

// Function to handle redirect to update screen
function redirectToUpdate(incidentId) {
    window.location.href = `incident-update.html?id=${incidentId}`;
}

// Initial load of incidents
window.onload = loadIncidents;
