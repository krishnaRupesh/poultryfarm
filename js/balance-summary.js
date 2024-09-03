function loadBalanceSummary() {
    const customerName = document.getElementById('customer-name').value;
    if (customerName) {
        // Fetch remaining balance for the customer
        const remainingBalance = getRemainingBalance(customerName);
        document.getElementById('remaining-balance').value = remainingBalance;
    } else {
        alert('Please select a customer.');
    }
}

function getRemainingBalance(customerName) {
    // Placeholder for actual logic to fetch remaining balance from the database
    return 500; // Example remaining balance
}
