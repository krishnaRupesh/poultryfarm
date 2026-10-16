document.getElementById('new-incident-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const form = event.currentTarget;
    const data = formPayload(form);
    const payload = {
        name: data.name,
        incident_type: data['incident-type'],
        incident_date: data['incident-date'],
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

document.addEventListener('DOMContentLoaded', () => setDefaultDate('incident-date'));
