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
            row.innerHTML = `<td>${detail.date}</td><td>${detail.id}</td><td>${detail.amount}</td>`;
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
        { date: '2024-09-01', id: 'ORD123', amount: '100' },
        { date: '2024-09-02', id: 'PAY456', amount: '-50' }
    ]; // Example details
}
