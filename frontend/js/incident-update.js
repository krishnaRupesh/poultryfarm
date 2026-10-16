async function loadIncidentDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const incidentId = urlParams.get('id');

    if (!incidentId) {
        setStatus('Incident ID is required.', 'error');
        return;
    }

    try {
        const incident = await apiRequest(`/api/incidents/${incidentId}`);
        document.getElementById('incident-id').value = incident.incident_id;
        document.getElementById('incident-date').value = incident.incident_date;
        document.getElementById('name').value = incident.name;
        document.getElementById('incident-type').value = incident.incident_type;
        document.getElementById('amount-spent').value = incident.amount_spent;
        document.getElementById('summary').value = incident.summary || '';
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.getElementById('update-incident-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const data = formPayload(event.currentTarget);
    const incidentId = data['incident-id'];
    const payload = {
        name: data.name,
        incident_type: data['incident-type'],
        incident_date: data['incident-date'],
        amount_spent: data['amount-spent'],
        summary: data.summary || null,
        updated_by: DEFAULT_USER
    };

    try {
        await apiRequest(`/api/incidents/${incidentId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        setStatus('Incident updated successfully.');
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', loadIncidentDetails);
