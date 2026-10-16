async function loadProducts() {
    const tbody = document.getElementById('product-list');
    if (!tbody) {
        return;
    }

    try {
        const products = await apiRequest('/api/products/');
        tbody.innerHTML = products.map((product) => `
            <tr>
                <td>${product.product_name}</td>
                <td>${money(product.price)}</td>
                <td>${product.date || ''}</td>
            </tr>
        `).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

document.getElementById('product-form')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearStatus();

    const form = event.currentTarget;
    const data = formPayload(form);
    const payload = {
        product_name: data['product-name'],
        price: data.price,
        date: data.date,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/products/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Product saved successfully.');
        form.reset();
        setDefaultDate('date');
        await loadProducts();
    } catch (error) {
        setStatus(error.message, 'error');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate('date');
    loadProducts();
});
