async function loadMoreTransactions() {
    const tbody = document.getElementById('transaction-list');
    if (!tbody) {
        return;
    }

    clearStatus();
    try {
        const [orders, payments] = await Promise.all([
            apiRequest('/api/orders/'),
            apiRequest('/api/payments/')
        ]);

        const rows = [
            ...orders.map((order) => ({
                date: order.date,
                type: 'order',
                customer: order.customer_name,
                reference: order.order_id,
                amount: order.total_amount
            })),
            ...payments.map((payment) => ({
                date: payment.payment_date,
                type: 'payment',
                customer: payment.customer_name,
                reference: payment.payment_id,
                amount: payment.payment_amount
            }))
        ].sort((a, b) => b.date.localeCompare(a.date));

        tbody.innerHTML = rows.map((row) => `
            <tr class="${row.type === 'payment' ? 'payment-row' : 'order-row'}">
                <td>${row.date}</td>
                <td>${row.type}</td>
                <td>${row.customer || ''}</td>
                <td>${row.reference}</td>
                <td>${money(row.amount)}</td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

async function saveEggRate() {
    clearStatus();
    const date = document.getElementById('date').value;
    const rate = document.getElementById('rate').value;

    if (!date || !rate) {
        setStatus('Date and rate are required.', 'error');
        return;
    }

    try {
        await apiRequest('/api/products/', {
            method: 'POST',
            body: JSON.stringify({
                product_name: 'Egg',
                price: rate,
                date,
                created_by: DEFAULT_USER
            })
        });
        setStatus('Egg rate saved.');
        document.getElementById('egg-rate-form').reset();
        setDefaultDate('date');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

async function loadMoreEggRates() {
    const tbody = document.getElementById('egg-rate-history');
    if (!tbody) {
        return;
    }

    clearStatus();
    try {
        const products = await apiRequest('/api/products/');
        const eggRates = products.filter((product) => product.product_name.toLowerCase() === 'egg');
        tbody.innerHTML = eggRates.map((rate) => `
            <tr>
                <td>${rate.date}</td>
                <td>${money(rate.price)}</td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate('date');
    loadMoreTransactions();
    loadMoreEggRates();
});
