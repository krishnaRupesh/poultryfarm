function loadBalanceDetails() {
    const customerName = document.getElementById('customer-name').value;
    if (customerName) {
        // Fetch remaining balance and details for the customer
        const remainingBalance = getRemainingBalance(customerName);
        document.getElementById('remaining-balance').value = remainingBalance;

        const details = getBalanceDetails(customerName);
        const tbody = document.getElementById('balance-details');
        tbody.innerHTML = ''; // Clear previous details

        details.forEach(detail => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${detail.date}</td>
                <td>${detail.id}</td>
                <td>${detail.quantity}</td>
                <td>${detail.amount}</td>
                <td>${detail.type}</td>
            `;
            row.className = detail.type === 'payment' ? 'payment-row' : 'order-row';
            tbody.appendChild(row);
        });
    } else {
        alert('Please select a customer.');
    }
}

function getRemainingBalance(customerName) {
    // Placeholder for actual logic to fetch remaining balance from the database
    return 500; // Example remaining balance
}

function getBalanceDetails(customerName) {
    // Placeholder for actual logic to fetch balance details from the database
    return [
        { date: '2024-09-01', id: 'ORD123', quantity: '10', amount: '100', type: 'order' },
        { date: '2024-09-02', id: 'PAY456', quantity: '', amount: '-50', type: 'payment' }
    ]; // Example details
}
