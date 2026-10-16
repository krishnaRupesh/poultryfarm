async function populatePaymentCustomers() {
    const select = document.getElementById('customer-name');
    const customers = await apiRequest('/api/customers/');
    populateSelect(
        select,
        customers,
        (customer) => customer.customer_id,
        (customer) => customer.customer_name,
        'Select Customer'
    );
}

document.getElementById('payment-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const form = event.currentTarget;
    const data = formPayload(form);
    const payload = {
        customer_id: data['customer-name'],
        payment_amount: data['payment-amount'],
        payment_date: data['payment-date'],
        payment_mode: data['payment-mode'],
        remarks: data.remarks || null,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/payments/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Payment saved successfully.');
        form.reset();
        setDefaultDate('payment-date');
        await populatePaymentCustomers();
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    setDefaultDate('payment-date');
    try {
        await populatePaymentCustomers();
    } catch (error) {
        setStatus(error.message, 'error');
    }
});
