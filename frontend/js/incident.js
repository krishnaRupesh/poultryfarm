document.getElementById('new-incident-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();
    const data = formPayload(event.currentTarget);

    try {
        await apiRequest('/api/incidents/', {
            method: 'POST',
            body: JSON.stringify({
                name: data.name,
                incident_type: data['incident-type'],
                incident_date: data['incident-date'],
                summary: data.summary || null,
                amount_spent: data['amount-spent'],
                created_by: DEFAULT_USER
            })
        });
        setStatus('Incident saved successfully.');
    } catch (error) {
        setStatus(error.message, 'error');
    }
});
