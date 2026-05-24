// Function to fetch and display customer balance summary
function loadBalanceSummary() {
    const data = getCustomerBalanceSummary();
    const tbody = document.getElementById('balance-summary');
    tbody.innerHTML = ''; // Clear previous summary

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.customerName}</td><td>${item.remainingBalance}</td>`;
        tbody.appendChild(row);
    });

    // Update last updated time
    document.getElementById('last-updated-time').textContent = getLastUpdatedTime();
}

// Function to simulate fetching data from backend
function getCustomerBalanceSummary() {
    // Placeholder for actual logic to fetch customer balance summary from the backend
    return [
        { customerName: 'John Doe', remainingBalance: '150' },
        { customerName: 'Jane Smith', remainingBalance: '100' },
        { customerName: 'Acme Corp', remainingBalance: '250' }
    ].sort((a, b) => b.remainingBalance - a.remainingBalance); // Sort by remaining balance descending
}

// Function to simulate fetching the last updated time
function getLastUpdatedTime() {
    // Placeholder for actual logic to fetch last updated time from the backend
    return new Date().toLocaleTimeString();
}

// Function to handle the refresh button click
function refreshData() {
    alert('Data refreshed!');
    loadBalanceSummary();
}

// Initial load of balance summary
window.onload = loadBalanceSummary;
