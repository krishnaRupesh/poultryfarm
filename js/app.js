let transactions = [];
let eggRates = [];
let products = [
    { name: "Egg", basePrice: 5 },
    { name: "Chicken", basePrice: 10 }
];
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

let customers = [];

function registerCustomer() {
    const name = document.getElementById('customer-name').value;
    const email = document.getElementById('customer-email').value;
    const phone = document.getElementById('customer-phone').value;
    const address = document.getElementById('customer-address').value;

    if (name && email && phone && address) {
        customers.push({ name, email, phone, address });
        alert('Customer registered successfully!');
        clearCustomerForm();
    } else {
        alert('Please fill out all fields.');
    }
}

function clearCustomerForm() {
    document.getElementById('customer-form').reset();
}

// Function to initialize the product dropdown
function initializeProductOptions() {
    const productSelect = document.getElementById('product');
    products.forEach(product => {
        const option = document.createElement('option');
        option.value = product.name;
        option.textContent = product.name;
        productSelect.appendChild(option);
    });
}

// Function to update the product price based on selected date and product
function updateProductPrice() {
    const date = document.getElementById('sale-date').value;
    const productName = document.getElementById('product').value;
    const priceInput = document.getElementById('price');

    if (date && productName) {
        const product = products.find(p => p.name === productName);
        if (product) {
            const adjustedPrice = getAdjustedPrice(product, date);
            priceInput.value = adjustedPrice.toFixed(2);
        }
    } else {
        priceInput.value = '';
    }
}

// Simulated function to adjust the price based on the date
function getAdjustedPrice(product, date) {
    const basePrice = product.basePrice;
    const daysSinceStart = Math.floor((new Date(date) - new Date("2024-01-01")) / (1000 * 60 * 60 * 24));
    return basePrice + daysSinceStart * 0.1;
}

function addProductToOrder() {
    const product = document.getElementById('product').value;
    const quantity = document.getElementById('quantity').value;
    const originalPrice = document.getElementById('price').value;
    const customPrice = document.getElementById('custom-price').value || originalPrice;
    const remarks = document.getElementById('remarks').value;

    if (product && quantity && originalPrice) {
        const discount = (originalPrice - customPrice).toFixed(2);
        const orderSummary = document.getElementById('order-summary');
        const li = document.createElement('li');
        li.textContent = `${product} - Quantity: ${quantity} - Original Price: $${originalPrice} - Custom Price: $${customPrice} - Discount: $${discount} - Remarks: ${remarks}`;
        orderSummary.appendChild(li);
    }
}

function submitOrder() {
    // Logic to submit the order
    alert('Order Submitted');
}

// Initialize the product options when the page loads
window.onload = initializeProductOptions;

// Function to initialize the product and customer dropdowns
function initializeProductOptions() {
    const productSelect = document.getElementById('product');
    products.forEach(product => {
        const option = document.createElement('option');
        option.value = product.name;
        option.textContent = product.name;
        productSelect.appendChild(option);
    });
    fetchCustomerData(); // Fetch and populate customer dropdown
}

function fetchCustomerData() {
    // Simulate fetching customer data from a backend or local source
    // Replace this with an actual API call if you have a backend
    customers = [
        { id: 1, name: "John Doe" },
        { id: 2, name: "Jane Smith" }
    ];

    const customerSelect = document.getElementById('customer');
    customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        option.textContent = customer.name;
        customerSelect.appendChild(option);
    });
}

// Function to update the product price based on selected date and product
function updateProductPrice() {
    const date = document.getElementById('sale-date').value;
    const productName = document.getElementById('product').value;
    const priceInput = document.getElementById('price');

    if (date && productName) {
        const product = products.find(p => p.name === productName);
        if (product) {
            const adjustedPrice = getAdjustedPrice(product, date);
            priceInput.value = adjustedPrice.toFixed(2);
        }
    } else {
        priceInput.value = '';
    }
}

// Simulated function to adjust the price based on the date
function getAdjustedPrice(product, date) {
    const basePrice = product.basePrice;
    const daysSinceStart = Math.floor((new Date(date) - new Date("2024-01-01")) / (1000 * 60 * 60 * 24));
    return basePrice + daysSinceStart * 0.1;
}

function addProductToOrder() {
    const customerId = document.getElementById('customer').value;
    const customerName = customers.find(c => c.id == customerId)?.name || 'Unknown';
    const product = document.getElementById('product').value;
    const quantity = document.getElementById('quantity').value;
    const originalPrice = document.getElementById('price').value;
    const customPrice = document.getElementById('custom-price').value || originalPrice;
    const remarks = document.getElementById('remarks').value;

    if (product && quantity && originalPrice) {
        const discount = (originalPrice - customPrice).toFixed(2);
        const orderSummary = document.getElementById('order-summary');
        const li = document.createElement('li');
        li.textContent = `${customerName} - ${product} - Quantity: ${quantity} - Original Price: $${originalPrice} - Custom Price: $${customPrice} - Discount: $${discount} - Remarks: ${remarks}`;
        orderSummary.appendChild(li);
    }
}

function submitOrder() {
    // Logic to submit the order
    alert('Order Submitted');
}

// Initialize the product options and customer dropdown when the page loads
window.onload = initializeProductOptions;
