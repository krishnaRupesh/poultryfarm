let orderProducts = [];
let saleDraft = null;

function orderDateField() {
    return document.getElementById('order-date') || document.getElementById('sale-date');
}

function customerField() {
    return document.getElementById('customer-name') || document.getElementById('customer');
}

function productField() {
    return document.getElementById('product');
}

function selectedProduct() {
    const id = Number(productField()?.value);
    return orderProducts.find((product) => product.product_id === id);
}

async function populateOrderCustomers() {
    const select = customerField();
    if (!select) {
        return;
    }

    const customers = await apiRequest('/api/customers/');
    populateSelect(
        select,
        customers,
        (customer) => customer.customer_id,
        (customer) => customer.customer_name,
        'Select Customer'
    );
}

async function populateOrderProducts() {
    const select = productField();
    const date = orderDateField()?.value;
    if (!select || !date) {
        return;
    }

    const products = await apiRequest('/api/products/');
    orderProducts = products.filter((product) => product.date === date);
    populateSelect(
        select,
        orderProducts,
        (product) => product.product_id,
        (product) => `${product.product_name} - ${money(product.price)}`,
        orderProducts.length ? 'Select Product' : 'No products priced for this date'
    );
    document.getElementById('price').value = '';
    calculateTotalAmount();
}

function updateProductPrice() {
    const product = selectedProduct();
    document.getElementById('price').value = product ? money(product.price) : '';
    calculateTotalAmount();
}

function calculateTotalAmount() {
    const price = Number(document.getElementById('price')?.value || 0);
    const discountPrice = Number(document.getElementById('discount-price')?.value || document.getElementById('custom-price')?.value || price);
    const quantity = Number(document.getElementById('quantity')?.value || 0);
    const total = quantity ? discountPrice * quantity : 0;
    const totalField = document.getElementById('total-amount');
    if (totalField) {
        totalField.value = total ? money(total) : '';
    }
}

function orderPayload() {
    const product = selectedProduct();
    return {
        customer_id: customerField().value,
        product_id: product?.product_id,
        date: orderDateField().value,
        quantity: document.getElementById('quantity').value,
        discount_price: document.getElementById('discount-price')?.value || document.getElementById('custom-price')?.value || null,
        remarks: document.getElementById('remarks')?.value || null,
        created_by: DEFAULT_USER
    };
}

async function saveOrder(payload) {
    await apiRequest('/api/orders/', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
}

function addProductToOrder() {
    clearStatus();
    const product = selectedProduct();
    if (!product || !customerField().value || !document.getElementById('quantity').value) {
        setStatus('Select customer, date, product, and quantity before adding the order.', 'error');
        return;
    }

    saleDraft = orderPayload();
    const orderSummary = document.getElementById('order-summary');
    if (orderSummary) {
        orderSummary.innerHTML = `
            <li>${product.product_name} - Quantity: ${saleDraft.quantity} - Price: ${money(product.price)} - Total: ${money((saleDraft.discount_price || product.price) * saleDraft.quantity)}</li>
        `;
    }
}

async function submitOrder() {
    clearStatus();
    try {
        await saveOrder(saleDraft || orderPayload());
        setStatus('Order saved successfully.');
        document.getElementById('sale-form')?.reset();
        document.getElementById('order-summary').innerHTML = '';
        saleDraft = null;
        setDefaultDate('sale-date');
        await populateOrderProducts();
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.getElementById('order-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();
    try {
        await saveOrder(orderPayload());
        setStatus('Order saved successfully.');
        event.currentTarget.reset();
        setDefaultDate('order-date');
        await populateOrderProducts();
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    setDefaultDate('order-date');
    setDefaultDate('sale-date');
    try {
        await populateOrderCustomers();
        await populateOrderProducts();
    } catch (error) {
        setStatus(error.message, 'error');
    }

    orderDateField()?.addEventListener('change', populateOrderProducts);
    productField()?.addEventListener('change', updateProductPrice);
    document.getElementById('quantity')?.addEventListener('input', calculateTotalAmount);
    document.getElementById('discount-price')?.addEventListener('input', calculateTotalAmount);
    document.getElementById('custom-price')?.addEventListener('input', calculateTotalAmount);
});
