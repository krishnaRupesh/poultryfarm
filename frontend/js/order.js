document.getElementById('order-form').addEventListener('submit', function(event) {
    event.preventDefault();
    // Add logic to save order to database
    alert('Order added successfully!');
});

function updateProductPrice() {
    const product = document.getElementById('product').value;
    const orderDate = document.getElementById('order-date').value;
    
    if (product && orderDate) {
        // Fetch the price for the selected product on the given date
        const price = getProductPrice(product, orderDate);
        if (price !== null) {
            document.getElementById('price').value = price;
            calculateTotalAmount();
        } else {
            alert('Price not available for the selected date.');
        }
    }
}

function getProductPrice(product, date) {
    // Placeholder for actual logic to fetch price from the database
    // Return null if price not available
    return 10.0; // Example price
}

function calculateTotalAmount() {
    const price = parseFloat(document.getElementById('price').value);
    const discountPrice = parseFloat(document.getElementById('discount-price').value) || price;
    const quantity = parseFloat(document.getElementById('quantity').value);

    const totalAmount = (discountPrice * quantity).toFixed(2);
    document.getElementById('total-amount').value = totalAmount;
}
