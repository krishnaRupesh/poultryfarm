// Function to load incident details based on ID
function loadIncidentDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const incidentId = urlParams.get('id');

    if (incidentId) {
        const incident = getIncidentById(incidentId);
        if (incident) {
            document.getElementById('incident-id').value = incident.id;
            document.getElementById('incident-date').value = incident.date;
            document.getElementById('name').value = incident.name;
            document.getElementById('incident-type').value = incident.type;
            document.getElementById('amount-spent').value = incident.amountSpent;
            document.getElementById('summary').value = incident.summary;
        } else {
            alert('Incident not found.');
        }
    }
}

// Function to simulate fetching an incident by ID from backend
function getIncidentById(incidentId) {
    const incidents = getIncidents(); // Assuming getIncidents is available globally
    return incidents.find(incident => incident.id === incidentId);
}

// Handle form submission for updating the incident
document.getElementById('update-incident-form').addEventListener('submit', function(event) {
    event.preventDefault();
    // Code to handle form submission and update the incident data
    alert('Incident Updated!');
});

// Load incident details on page load
window.onload = loadIncidentDetails;
