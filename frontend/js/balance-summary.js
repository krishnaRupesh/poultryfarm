async function loadBalanceSummary() {
    clearStatus();
    const tbody = document.getElementById('balance-summary');

    try {
        const data = await apiRequest('/api/customer-balances/summary');
        tbody.innerHTML = data.map((item) => `
            <tr>
                <td><a href="customer-balance-sheet-details.html?customer_id=${item.customer_id}">${item.customer_name || ''}</a></td>
                <td>${money(item.remaining_balance)}</td>
            </tr>
        `).join('');

        const lastUpdated = data[0]?.last_updated || null;
        document.getElementById('last-updated-time').textContent = lastUpdated
            ? new Date(lastUpdated).toLocaleString()
            : '--:--';
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

async function refreshData() {
    clearStatus();
    try {
        await apiRequest('/api/customer-balances/refresh', {
            method: 'POST',
            body: JSON.stringify({ updated_by: DEFAULT_USER })
        });
        setStatus('Balance summary refreshed.');
        await loadBalanceSummary();
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', loadBalanceSummary);
