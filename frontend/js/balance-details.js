async function populateBalanceCustomers() {
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

async function loadBalanceDetails(customerId = null) {
    clearStatus();
    const selectedCustomer = customerId || document.getElementById('customer-name').value;
    if (!selectedCustomer) {
        setStatus('Please select a customer.', 'error');
        return;
    }

    try {
        const details = await apiRequest(`/api/customer-balances/${selectedCustomer}/details`);
        document.getElementById('customer-name').value = details.customer_id;
        document.getElementById('remaining-balance').value = money(details.remaining_balance);

        const tbody = document.getElementById('balance-details');
        tbody.innerHTML = details.details.map((detail) => `
            <tr class="${detail.type === 'payment' ? 'payment-row' : 'order-row'}">
                <td>${detail.date}</td>
                <td>${detail.id}</td>
                <td>${detail.quantity || ''}</td>
                <td>${money(detail.amount)}</td>
                <td>${detail.type}</td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await populateBalanceCustomers();
        const customerId = new URLSearchParams(window.location.search).get('customer_id');
        if (customerId) {
            await loadBalanceDetails(customerId);
        }
    } catch (error) {
        setStatus(error.message, 'error');
    }
});
