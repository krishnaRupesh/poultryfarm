let allOrders = [];
let allCustomers = [];
let allPayments = [];
let allProducts = [];
let customerBalances = {};
let latestEggPrice = 0.075;

async function loadInitialData() {
    clearStatus();
    await Promise.all([
        loadCustomers(),
        loadProducts(),
        loadOrders(),
        loadPayments()
    ]);
    updateKpis();
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(tabName));
    if (btn) btn.classList.add('active');

    const content = document.getElementById(`tab-${tabName}`);
    if (content) content.classList.add('active');
}

// -----------------------------------------------------------------------------
// LOADERS
// -----------------------------------------------------------------------------
async function loadCustomers() {
    const showArchived = document.getElementById('show-archived-customers')?.checked;
    const url = showArchived ? '/api/customers/?include_deleted=true' : '/api/customers/';

    try {
        allCustomers = await apiRequest(url);
        // Also fetch balances
        try {
            const balances = await apiRequest('/api/customer-balances/');
            customerBalances = {};
            balances.forEach(b => {
                customerBalances[b.customer_id] = b.remaining_balance || 0;
            });
        } catch (_) {}

        renderCustomers();
        populateCustomerDropdowns();
    } catch (err) {
        setStatus(`Failed to load customers: ${err.message}`, 'error');
    }
}

async function loadProducts() {
    try {
        allProducts = await apiRequest('/api/products/');
        renderRates();
        populateProductDropdown();
        // Extract latest egg rate
        const eggProduct = allProducts.find(p => p.product_name.toLowerCase().includes('egg'));
        if (eggProduct && eggProduct.price) {
            latestEggPrice = parseFloat(eggProduct.price);
        }
    } catch (err) {
        setStatus(`Failed to load products/rates: ${err.message}`, 'error');
    }
}

async function loadOrders() {
    const showArchived = document.getElementById('show-archived-orders')?.checked;
    const url = showArchived ? '/api/orders/?include_deleted=true' : '/api/orders/';

    try {
        allOrders = await apiRequest(url);
        renderOrders();
        updateKpis();
    } catch (err) {
        setStatus(`Failed to load orders: ${err.message}`, 'error');
    }
}

async function loadPayments() {
    const showArchived = document.getElementById('show-archived-payments')?.checked;
    const url = showArchived ? '/api/payments/?include_deleted=true' : '/api/payments/';

    try {
        allPayments = await apiRequest(url);
        renderPayments();
        updateKpis();
    } catch (err) {
        setStatus(`Failed to load payments: ${err.message}`, 'error');
    }
}

// -----------------------------------------------------------------------------
// RENDERERS
// -----------------------------------------------------------------------------
function renderOrders() {
    const tbody = document.getElementById('orders-table-body');
    const search = (document.getElementById('order-search')?.value || '').toLowerCase();

    const filtered = allOrders.filter(o => {
        if (!search) return true;
        const name = (o.customer_name || '').toLowerCase();
        const id = String(o.order_id);
        return name.includes(search) || id.includes(search);
    });

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #627d98; padding: 20px;">No sales orders found. Click "+ New Egg Sale" to log a sale.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(o => {
        const isArchived = o.is_deleted;
        const total = parseFloat(o.total_amount || 0);
        const qty = parseInt(o.quantity || 0);
        const trays = (qty / 30).toFixed(1);

        return `
            <tr style="${isArchived ? 'opacity: 0.6; background: #f8fafc;' : ''}">
                <td>#${o.order_id}</td>
                <td>${o.date || '--'}</td>
                <td><strong>${escapeHtml(o.customer_name || `Customer #${o.customer_id}`)}</strong></td>
                <td>${escapeHtml(o.product_name || 'Eggs')}</td>
                <td><strong>${qty.toLocaleString()} eggs</strong> <span style="font-size: 0.8rem; color: #627d98;">(${trays} trays)</span></td>
                <td>$${parseFloat(o.price || 0).toFixed(4)}</td>
                <td><strong style="color: #155724; font-size: 1.05rem;">$${total.toFixed(2)}</strong></td>
                <td style="font-size: 0.8rem; color: #627d98;">${escapeHtml(o.remarks || '')}</td>
                <td>
                    ${isArchived
                        ? `<button type="button" class="btn-sm" style="background: #10b981;" onclick="handleRestoreOrder(${o.order_id})">↩️ Restore</button>`
                        : `<button type="button" class="btn-sm btn-danger" onclick="handleDeleteOrder(${o.order_id})">Archive</button>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

function renderCustomers() {
    const tbody = document.getElementById('customers-table-body');
    const search = (document.getElementById('customer-search')?.value || '').toLowerCase();

    const filtered = allCustomers.filter(c => {
        if (!search) return true;
        return (c.customer_name || '').toLowerCase().includes(search) || (c.phone_number || '').includes(search);
    });

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #627d98; padding: 20px;">No customers found. Click "+ Register Customer" to add one.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(c => {
        const isArchived = c.is_deleted;
        const balance = customerBalances[c.customer_id] !== undefined ? customerBalances[c.customer_id] : 0;
        const balanceBadge = balance > 0
            ? `<span class="balance-badge-due">Due: $${parseFloat(balance).toFixed(2)}</span>`
            : `<span class="balance-badge-clear">Paid Clear ($0.00)</span>`;

        return `
            <tr style="${isArchived ? 'opacity: 0.6; background: #f8fafc;' : ''}">
                <td><strong>${escapeHtml(c.customer_name)}</strong></td>
                <td>${escapeHtml(c.phone_number || '--')}</td>
                <td style="font-size: 0.85rem; color: #627d98;">${escapeHtml(c.address || '--')}</td>
                <td>--</td>
                <td>--</td>
                <td>${balanceBadge}</td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        ${isArchived
                            ? `<button type="button" class="btn-sm" style="background: #10b981;" onclick="handleRestoreCustomer(${c.customer_id})">↩️ Restore</button>`
                            : `
                                <button type="button" class="btn-sm" style="background: #1f6feb;" onclick="openPaymentForCustomer(${c.customer_id})">💳 Collect $</button>
                                <button type="button" class="btn-sm secondary" onclick="openEditCustomerModal(${c.customer_id})">Edit</button>
                                <button type="button" class="btn-sm btn-danger" onclick="handleDeleteCustomer(${c.customer_id}, '${escapeHtml(c.customer_name)}')">Archive</button>
                            `
                        }
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderPayments() {
    const tbody = document.getElementById('payments-table-body');
    if (!allPayments || allPayments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #627d98; padding: 20px;">No payments recorded yet. Click "+ Record Payment" to log cash/online collections.</td></tr>';
        return;
    }

    tbody.innerHTML = allPayments.map(p => {
        const isArchived = p.is_deleted;
        const amount = parseFloat(p.payment_amount || 0);

        return `
            <tr style="${isArchived ? 'opacity: 0.6; background: #f8fafc;' : ''}">
                <td>#${p.payment_id}</td>
                <td>${p.payment_date || '--'}</td>
                <td><strong>${escapeHtml(p.customer_name || `Customer #${p.customer_id}`)}</strong></td>
                <td><strong style="color: #155724; font-size: 1.05rem;">$${amount.toFixed(2)}</strong></td>
                <td><span class="badge" style="background: #e0f2fe; color: #0369a1;">${escapeHtml(p.payment_mode || 'Cash')}</span></td>
                <td style="font-size: 0.8rem; color: #627d98;">${escapeHtml(p.remarks || '')}</td>
                <td>
                    ${isArchived
                        ? `<button type="button" class="btn-sm" style="background: #10b981;" onclick="handleRestorePayment(${p.payment_id})">↩️ Restore</button>`
                        : `<button type="button" class="btn-sm btn-danger" onclick="handleDeletePayment(${p.payment_id})">Archive</button>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

function renderRates() {
    const tbody = document.getElementById('rates-table-body');
    if (!allProducts || allProducts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #627d98; padding: 20px;">No rates published yet.</td></tr>';
        return;
    }

    tbody.innerHTML = allProducts.map(p => {
        const unitPrice = parseFloat(p.price || 0);
        return `
            <tr>
                <td>${p.date || '--'}</td>
                <td><strong>${escapeHtml(p.product_name)}</strong></td>
                <td><strong style="color: #0b69a3;">$${unitPrice.toFixed(4)}</strong></td>
                <td>$${(unitPrice * 30).toFixed(2)}</td>
                <td>$${(unitPrice * 100).toFixed(2)}</td>
                <td>${escapeHtml(p.created_by || 'system')}</td>
            </tr>
        `;
    }).join('');
}

// -----------------------------------------------------------------------------
// KPIS CALCULATION
// -----------------------------------------------------------------------------
function updateKpis() {
    const todayStr = today();

    // 1. Today's sales
    const todayOrders = allOrders.filter(o => !o.is_deleted && o.date === todayStr);
    const todaySalesSum = todayOrders.reduce((sum, o) => sum + parseFloat(o.total_amount || 0), 0);
    const todayEggsSum = todayOrders.reduce((sum, o) => sum + parseInt(o.quantity || 0), 0);

    document.getElementById('kpi-today-sales').textContent = `$${todaySalesSum.toFixed(2)}`;
    document.getElementById('kpi-today-eggs').textContent = `${todayEggsSum.toLocaleString()} eggs delivered`;

    // 2. Today's payments collected
    const todayPayments = allPayments.filter(p => !p.is_deleted && p.payment_date === todayStr);
    const todayPaySum = todayPayments.reduce((sum, p) => sum + parseFloat(p.payment_amount || 0), 0);
    document.getElementById('kpi-today-collections').textContent = `$${todayPaySum.toFixed(2)}`;

    // 3. Outstanding receivables
    let totalAR = 0;
    let debtorCount = 0;
    Object.values(customerBalances).forEach(b => {
        if (b > 0) {
            totalAR += b;
            debtorCount++;
        }
    });
    document.getElementById('kpi-total-receivables').textContent = `$${totalAR.toFixed(2)}`;
    document.getElementById('kpi-debtor-count').textContent = `${debtorCount} customers with dues`;

    // 4. Today's egg rate
    document.getElementById('kpi-egg-rate').textContent = `$${latestEggPrice.toFixed(4)} / egg`;
    document.getElementById('kpi-tray-rate').textContent = `$${(latestEggPrice * 30).toFixed(2)} / Tray (30)`;
}

// -----------------------------------------------------------------------------
// DROPDOWNS & AUTO-FILL
// -----------------------------------------------------------------------------
function populateCustomerDropdowns() {
    const active = allCustomers.filter(c => !c.is_deleted);
    const opts = '<option value="">-- Select Customer --</option>' + active.map(c => `
        <option value="${c.customer_id}">${escapeHtml(c.customer_name)} (${escapeHtml(c.phone_number || '')})</option>
    `).join('');

    const orderSel = document.getElementById('order-customer-id');
    if (orderSel) orderSel.innerHTML = opts;

    const paySel = document.getElementById('payment-customer-id');
    if (paySel) paySel.innerHTML = opts;
}

function populateProductDropdown() {
    const prodSel = document.getElementById('order-product-id');
    if (!prodSel) return;
    const active = allProducts.filter(p => !p.is_deleted);
    prodSel.innerHTML = active.map(p => `
        <option value="${p.product_id}" data-price="${p.price}">${escapeHtml(p.product_name)} ($${parseFloat(p.price || 0).toFixed(4)})</option>
    `).join('');
}

function onCustomerSelectChange() {
    const custId = document.getElementById('order-customer-id').value;
    const hint = document.getElementById('customer-balance-hint');
    if (custId && customerBalances[custId] !== undefined) {
        const bal = customerBalances[custId];
        hint.textContent = bal > 0 ? `Current Outstanding Due: $${bal.toFixed(2)}` : 'Account Clear ($0.00 due)';
        hint.style.color = bal > 0 ? '#b7791f' : '#155724';
    } else {
        hint.textContent = '';
    }
}

function onProductSelectChange() {
    const sel = document.getElementById('order-product-id');
    const opt = sel.options[sel.selectedIndex];
    if (opt && opt.dataset.price) {
        document.getElementById('order-unit-price').value = opt.dataset.price;
        calculateOrderTotal();
    }
}

function calculateOrderTotal() {
    const rawQty = parseFloat(document.getElementById('order-quantity').value) || 0;
    const unitType = document.getElementById('order-unit-type').value;
    const unitPrice = parseFloat(document.getElementById('order-unit-price').value) || 0;
    const discount = parseFloat(document.getElementById('order-discount').value) || 0;

    let totalEggs = rawQty;
    if (unitType === 'trays') {
        totalEggs = rawQty * 30;
    } else if (unitType === 'hundreds') {
        totalEggs = rawQty * 100;
    }

    const calculatedTotalEggsEl = document.getElementById('calculated-total-eggs');
    if (unitType !== 'eggs' && rawQty > 0) {
        calculatedTotalEggsEl.textContent = `= ${totalEggs.toLocaleString()} total single eggs`;
    } else {
        calculatedTotalEggsEl.textContent = '';
    }

    const subtotal = totalEggs * unitPrice;
    const finalTotal = Math.max(0, subtotal - discount);
    document.getElementById('order-display-total').textContent = `$${finalTotal.toFixed(2)}`;
}

// -----------------------------------------------------------------------------
// MODALS
// -----------------------------------------------------------------------------
function openOrderModal() {
    document.getElementById('order-form').reset();
    document.getElementById('order-date').value = today();
    document.getElementById('order-unit-price').value = latestEggPrice;
    document.getElementById('order-modal').classList.add('active');
    calculateOrderTotal();
}
function closeOrderModal() { document.getElementById('order-modal').classList.remove('active'); }

function openCustomerModal() {
    document.getElementById('customer-modal-title').textContent = 'Register New Customer';
    document.getElementById('customer-form').reset();
    document.getElementById('customer-id').value = '';
    document.getElementById('customer-modal').classList.add('active');
}
function openEditCustomerModal(custId) {
    const c = allCustomers.find(item => item.customer_id === custId);
    if (!c) return;
    document.getElementById('customer-modal-title').textContent = `Edit Customer: ${c.customer_name}`;
    document.getElementById('customer-id').value = c.customer_id;
    document.getElementById('customer-name').value = c.customer_name;
    document.getElementById('customer-phone').value = c.phone_number;
    document.getElementById('customer-email').value = c.email_id || '';
    document.getElementById('customer-address').value = c.address;
    document.getElementById('customer-modal').classList.add('active');
}
function closeCustomerModal() { document.getElementById('customer-modal').classList.remove('active'); }

function openPaymentModal() {
    document.getElementById('payment-form').reset();
    document.getElementById('payment-date').value = today();
    document.getElementById('payment-modal').classList.add('active');
}
function openPaymentForCustomer(custId) {
    openPaymentModal();
    document.getElementById('payment-customer-id').value = custId;
    if (customerBalances[custId] > 0) {
        document.getElementById('payment-amount').value = customerBalances[custId].toFixed(2);
    }
}
function closePaymentModal() { document.getElementById('payment-modal').classList.remove('active'); }

function openProductRateModal() {
    document.getElementById('rate-form').reset();
    document.getElementById('rate-date').value = today();
    document.getElementById('rate-price').value = latestEggPrice;
    updateRatePreviews();
    document.getElementById('rate-modal').classList.add('active');
}
function closeRateModal() { document.getElementById('rate-modal').classList.remove('active'); }

function updateRatePreviews() {
    const p = parseFloat(document.getElementById('rate-price').value) || 0;
    document.getElementById('preview-tray-price').textContent = `$${(p * 30).toFixed(2)}`;
    document.getElementById('preview-hundred-price').textContent = `$${(p * 100).toFixed(2)}`;
}

// -----------------------------------------------------------------------------
// FORM SUBMIT HANDLERS
// -----------------------------------------------------------------------------
async function handleSaveOrder(e) {
    e.preventDefault();
    clearStatus();

    const rawQty = parseFloat(document.getElementById('order-quantity').value) || 0;
    const unitType = document.getElementById('order-unit-type').value;
    let totalEggs = rawQty;
    if (unitType === 'trays') totalEggs = rawQty * 30;
    if (unitType === 'hundreds') totalEggs = rawQty * 100;

    const payload = {
        date: document.getElementById('order-date').value,
        customer_id: parseInt(document.getElementById('order-customer-id').value),
        product_id: parseInt(document.getElementById('order-product-id').value),
        quantity: totalEggs,
        discount_price: parseFloat(document.getElementById('order-discount').value) || 0,
        remarks: document.getElementById('order-remarks').value.trim() || null,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/orders/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Egg sale order recorded successfully.');
        closeOrderModal();
        await loadOrders();
        await loadCustomers();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleSaveCustomer(e) {
    e.preventDefault();
    clearStatus();

    const custId = document.getElementById('customer-id').value;
    const payload = {
        customer_name: document.getElementById('customer-name').value.trim(),
        phone_number: document.getElementById('customer-phone').value.trim(),
        email_id: document.getElementById('customer-email').value.trim() || null,
        address: document.getElementById('customer-address').value.trim(),
        created_by: DEFAULT_USER,
        updated_by: DEFAULT_USER
    };

    try {
        if (custId) {
            await apiRequest(`/api/customers/${custId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            setStatus(`Customer "${payload.customer_name}" updated.`);
        } else {
            await apiRequest('/api/customers/', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            setStatus(`Customer "${payload.customer_name}" registered successfully.`);
        }
        closeCustomerModal();
        await loadCustomers();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleSavePayment(e) {
    e.preventDefault();
    clearStatus();

    const payload = {
        customer_id: parseInt(document.getElementById('payment-customer-id').value),
        payment_date: document.getElementById('payment-date').value,
        payment_amount: parseFloat(document.getElementById('payment-amount').value),
        payment_mode: document.getElementById('payment-mode').value,
        remarks: document.getElementById('payment-remarks').value.trim() || null,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/payments/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus(`Payment of $${payload.payment_amount.toFixed(2)} recorded.`);
        closePaymentModal();
        await loadPayments();
        await loadCustomers();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleSaveRate(e) {
    e.preventDefault();
    clearStatus();

    const payload = {
        product_name: document.getElementById('rate-product-name').value.trim(),
        price: parseFloat(document.getElementById('rate-price').value),
        date: document.getElementById('rate-date').value,
        created_by: DEFAULT_USER
    };

    try {
        await apiRequest('/api/products/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        setStatus('Daily egg rate published.');
        closeRateModal();
        await loadProducts();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// DELETE & RESTORE ACTIONS
// -----------------------------------------------------------------------------
async function handleDeleteOrder(id) {
    if (!confirm('Are you sure you want to archive this order?')) return;
    try {
        await apiRequest(`/api/orders/${id}?deleted_by=${DEFAULT_USER}`, { method: 'DELETE' });
        setStatus('Order archived.');
        await loadOrders();
    } catch (err) { setStatus(err.message, 'error'); }
}
async function handleRestoreOrder(id) {
    try {
        await apiRequest(`/api/orders/${id}/restore`, { method: 'POST' });
        setStatus('Order restored.');
        await loadOrders();
    } catch (err) { setStatus(err.message, 'error'); }
}

async function handleDeleteCustomer(id, name) {
    if (!confirm(`Are you sure you want to archive customer "${name}"?`)) return;
    try {
        await apiRequest(`/api/customers/${id}?deleted_by=${DEFAULT_USER}`, { method: 'DELETE' });
        setStatus(`Customer "${name}" archived.`);
        await loadCustomers();
    } catch (err) { setStatus(err.message, 'error'); }
}
async function handleRestoreCustomer(id) {
    try {
        await apiRequest(`/api/customers/${id}/restore`, { method: 'POST' });
        setStatus('Customer restored.');
        await loadCustomers();
    } catch (err) { setStatus(err.message, 'error'); }
}

async function handleDeletePayment(id) {
    if (!confirm('Are you sure you want to archive this payment receipt?')) return;
    try {
        await apiRequest(`/api/payments/${id}?deleted_by=${DEFAULT_USER}`, { method: 'DELETE' });
        setStatus('Payment archived.');
        await loadPayments();
        await loadCustomers();
    } catch (err) { setStatus(err.message, 'error'); }
}
async function handleRestorePayment(id) {
    try {
        await apiRequest(`/api/payments/${id}/restore`, { method: 'POST' });
        setStatus('Payment restored.');
        await loadPayments();
        await loadCustomers();
    } catch (err) { setStatus(err.message, 'error'); }
}

function filterOrders() { renderOrders(); }
function filterCustomers() { renderCustomers(); }

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', loadInitialData);
