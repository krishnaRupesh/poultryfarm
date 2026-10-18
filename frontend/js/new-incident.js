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
                opt.textContent = `${b.batch_name} [${b.shed_name || 'No Shed'}] (${b.current_birds || 0} birds)`;
                batchSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.warn('Could not load sheds or batches:', err);
    }
}

document.getElementById('batch-id')?.addEventListener('change', (e) => {
    const selectedBatchId = parseInt(e.target.value);
    if (!selectedBatchId) return;
    const batch = allBatches.find(b => b.batch_id === selectedBatchId);
    if (batch && batch.shed_id) {
        const shedSelect = document.getElementById('shed-id');
        if (shedSelect) shedSelect.value = batch.shed_id;
    }
});

document.getElementById('new-incident-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const form = event.currentTarget;
    const data = formPayload(form);
    const shedVal = data['shed-id'];
    const batchVal = data['batch-id'];

    const payload = {
        name: data.name,
        incident_type: data['incident-type'],
        incident_date: data['incident-date'],
        shed_id: shedVal ? parseInt(shedVal) : null,
        batch_id: batchVal ? parseInt(batchVal) : null,
        summary: data.summary || null,
        amount_spent: data['amount-spent'],
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/incidents/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Incident created successfully.');
        form.reset();
        setDefaultDate('incident-date');
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate('incident-date');
    loadShedsAndBatches();
});
