let transactions = [];
let eggRates = [];
let products = [];
let currentPage = 1;

function addProductToOrder() {
    const product = document.getElementById('product').value;
    const quantity = document.getElementById('quantity').value;

    if (product && quantity) {
        const orderSummary = document.getElementById('order-summary');
        const li = document.createElement('li');
        li.textContent = `${product} - Quantity: ${quantity}`;
        orderSummary.appendChild(li);
    }
}

function submitOrder() {
    // Logic to submit the order
    alert('Order Submitted');
}

function loadMoreTransactions() {
    // Fetch and display more transactions
    const transactionList = document.getElementById('transaction-list');
    for (let i = 0; i < 5; i++) {
        const li = document.createElement('li');
        li.textContent = `Transaction ${currentPage * 5 + i + 1}`;
        transactionList.appendChild(li);
    }
    currentPage++;
}

function saveEggRate() {
    const date = document.getElementById('date').value;
    const rate = document.getElementById('rate').value;

    if (date && rate) {
        eggRates.push({ date, rate });
        alert('Egg rate saved');
    }
}

function loadMoreEggRates() {
    const eggRateHistory = document.getElementById('egg-rate-history');
    eggRates.slice((currentPage - 1) * 5, currentPage * 5).forEach(rate => {
        const li = document.createElement('li');
        li.textContent = `Date: ${rate.date}, Rate: ${rate.rate}`;
        eggRateHistory.appendChild(li);
    });
    currentPage++;
}

function saveProduct() {
    const productName = document.getElementById('product-name').value;
    const unit = document.getElementById('unit').value;
    const basePrice = document.getElementById('base-price').value;

    if (productName && unit && basePrice) {
        products.push({ productName, unit, basePrice });
        alert('Product saved');
    }
}
