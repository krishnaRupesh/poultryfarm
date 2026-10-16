async function loadCustomers() {
    const tbody = document.getElementById('customer-list');
    if (!tbody) {
        return;
    }

    try {
        const customers = await apiRequest('/api/customers/');
        tbody.innerHTML = customers.map((customer) => `
            <tr>
                <td>${customer.customer_name}</td>
                <td>${customer.phone_number}</td>
                <td>${customer.email_id || ''}</td>
                <td>${customer.address}</td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.getElementById('customer-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const form = event.currentTarget;
    const data = formPayload(form);
    const payload = {
        customer_name: data['customer-name'],
        phone_number: data['phone-number'] || data['customer-phone'],
        address: data.address || data['customer-address'],
        email_id: data['email-id'] || data['customer-email'] || null,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/customers/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Customer saved successfully.');
        form.reset();
        await loadCustomers();
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', loadCustomers);
