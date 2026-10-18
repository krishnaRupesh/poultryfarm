let allBatches = [];

async function loadShedsAndBatches() {
    try {
        const [sheds, batches] = await Promise.all([
            apiRequest('/api/flock/sheds'),
            apiRequest('/api/flock/batches')
        ]);

        allBatches = batches || [];
        const shedSelect = document.getElementById('shed-id');
        if (shedSelect) {
            sheds.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.shed_id;
                opt.textContent = `${s.shed_name} (${s.shed_type || 'General'})`;
                shedSelect.appendChild(opt);
            });
        }

        const batchSelect = document.getElementById('batch-id');
        if (batchSelect) {
            batches.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.batch_id;
                opt.textContent = `${b.batch_name} [${b.shed_name || 'No Shed'}]`;
                batchSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.warn('Could not load sheds or batches:', err);
    }
}

async function loadIncidentDetails() {
    await loadShedsAndBatches();

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
        if (incident.shed_id) {
            document.getElementById('shed-id').value = incident.shed_id;
        }
        if (incident.batch_id) {
            document.getElementById('batch-id').value = incident.batch_id;
        }
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.getElementById('update-incident-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const data = formPayload(event.currentTarget);
    const incidentId = data['incident-id'];
    const shedVal = data['shed-id'];
    const batchVal = data['batch-id'];

    const payload = {
        name: data.name,
        incident_type: data['incident-type'],
        incident_date: data['incident-date'],
        shed_id: shedVal ? parseInt(shedVal) : null,
        batch_id: batchVal ? parseInt(batchVal) : null,
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
