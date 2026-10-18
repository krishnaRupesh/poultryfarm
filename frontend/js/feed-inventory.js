let inventoryItems = [];
let allPurchases = [];

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');

    const activeContent = document.getElementById(tabId);
    if (activeContent) activeContent.classList.add('active');

    if (tabId === 'history-tab') {
        loadPurchases();
    }
}

async function loadFeedInventory() {
    clearStatus();
    try {
        const showArchived = document.getElementById('show-archived-items')?.checked;
        const url = showArchived ? '/api/feed/items?include_deleted=true' : '/api/feed/items';
        inventoryItems = await apiRequest(url);
        updateInventoryKPIs();
        renderInventoryTable(inventoryItems);
        populateCategoryFilter();
        populateItemDropdowns();
    } catch (err) {
        setStatus(err.message, 'error');
        document.getElementById('inventory-table-body').innerHTML = `<tr><td colspan="9" style="text-align: center; color: #dc3545;">Failed to load inventory: ${err.message}</td></tr>`;
    }
}

function updateInventoryKPIs() {
    let totalKg = 0;
    let totalVal = 0;
    let lowStockCount = 0;

    inventoryItems.filter(i => !i.is_deleted).forEach(item => {
        totalKg += item.current_stock_kg || 0;
        totalVal += item.total_valuation || 0;
        if (item.is_low_stock) {
            lowStockCount++;
        }
    });

    const totalMT = (totalKg / 1000.0).toFixed(2);

    document.getElementById('kpi-total-stock').textContent = `${totalMT} MT`;
    document.getElementById('kpi-total-stock-kg').textContent = `${totalKg.toLocaleString()} kg total in stock`;
    document.getElementById('kpi-total-valuation').textContent = `$${totalVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('kpi-item-count').textContent = inventoryItems.filter(i => !i.is_deleted).length;
    document.getElementById('kpi-low-stock').textContent = lowStockCount;
}

function renderInventoryTable(items) {
    const tbody = document.getElementById('inventory-table-body');
    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: #627d98;">No feed ingredients found. Click "+ Add New Feed Ingredient" to start.</td></tr>`;
        return;
    }

    tbody.innerHTML = items.map(item => {
        const isDel = item.is_deleted;
        const isLow = item.is_low_stock;
        let statusBadge = isLow
            ? `<span class="badge badge-lowstock">Low Stock (≤ ${item.reorder_level_kg} kg)</span>`
            : `<span class="badge badge-instock">In Stock</span>`;
        if (isDel) {
            statusBadge = `<span class="badge" style="background: #fee2e2; color: #991b1b;">Deleted</span>`;
        }

        const actionHtml = isDel
            ? `<button type="button" class="btn-sm" style="background: #16a34a; color: white;" onclick="handleRestoreItem(${item.item_id}, '${escapeHtml(item.name)}')">↩️ Restore</button>`
            : `
                <button type="button" class="btn-sm btn-warning" onclick="openEditModal(${item.item_id})">Edit</button>
                <button type="button" class="btn-sm btn-danger" onclick="handleDeleteItem(${item.item_id}, '${escapeHtml(item.name)}')">Delete</button>
              `;

        return `
            <tr style="${isDel ? 'opacity: 0.65; background: #fafafa;' : ''}">
                <td><strong>${escapeHtml(item.name)}</strong></td>
                <td><span style="color: #486581;">${escapeHtml(item.category || 'General')}</span></td>
                <td><strong style="color: #102a43;">${(item.current_stock_mt || 0).toFixed(3)} MT</strong></td>
                <td>${(item.current_stock_kg || 0).toLocaleString()} kg</td>
                <td>$${(item.average_cost_per_kg || 0).toFixed(4)}</td>
                <td>$${(item.average_cost_per_mt || 0).toFixed(2)}</td>
                <td><strong>$${(item.total_valuation || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
                <td>${statusBadge}</td>
                <td>${actionHtml}</td>
            </tr>
        `;
    }).join('');
}

function populateCategoryFilter() {
    const select = document.getElementById('category-filter');
    const categories = Array.from(new Set(inventoryItems.map(i => i.category || 'General'))).sort();
    select.innerHTML = '<option value="">All Categories</option>' +
        categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
}

function populateItemDropdowns() {
    const purchaseSelect = document.getElementById('purchase-item-id');
    const historySelect = document.getElementById('history-filter-item');

    const options = inventoryItems.map(i =>
        `<option value="${i.item_id}">${escapeHtml(i.name)} (Stock: ${(i.current_stock_mt || 0).toFixed(2)} MT / ${i.current_stock_kg} kg)</option>`
    ).join('');

    purchaseSelect.innerHTML = '<option value="">Select ingredient...</option>' + options;
    historySelect.innerHTML = '<option value="">All Items</option>' +
        inventoryItems.map(i => `<option value="${i.item_id}">${escapeHtml(i.name)}</option>`).join('');
}

function filterInventoryTable() {
    const search = document.getElementById('inventory-search').value.toLowerCase().trim();
    const category = document.getElementById('category-filter').value;

    const filtered = inventoryItems.filter(item => {
        const matchesSearch = !search || item.name.toLowerCase().includes(search);
        const matchesCategory = !category || (item.category || 'General') === category;
        return matchesSearch && matchesCategory;
    });

    renderInventoryTable(filtered);
}

// -----------------------------------------------------------------------------
// ADD INGREDIENT MODAL
// -----------------------------------------------------------------------------
function openAddModal() {
    document.getElementById('add-item-form').reset();
    document.getElementById('add-modal').classList.add('active');
}

function closeAddModal() {
    document.getElementById('add-modal').classList.remove('active');
}

async function handleCreateItem(e) {
    e.preventDefault();
    clearStatus();

    const name = document.getElementById('add-name').value.trim();
    const category = document.getElementById('add-category').value;
    const reorder = parseFloat(document.getElementById('add-reorder').value) || 100;
    const initialStock = parseFloat(document.getElementById('add-initial-stock').value) || 0;
    const initialCost = parseFloat(document.getElementById('add-initial-cost').value) || 0;

    try {
        await apiRequest('/api/feed/items', {
            method: 'POST',
            body: JSON.stringify({
                name,
                category,
                reorder_level_kg: reorder,
                current_stock_kg: initialStock,
                average_cost_per_kg: initialCost,
                created_by: DEFAULT_USER
            })
        });

        closeAddModal();
        setStatus(`Ingredient "${name}" created successfully!`);
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// EDIT INGREDIENT MODAL
// -----------------------------------------------------------------------------
function openEditModal(itemId) {
    const item = inventoryItems.find(i => i.item_id === itemId);
    if (!item) return;

    document.getElementById('edit-item-id').value = item.item_id;
    document.getElementById('edit-name').value = item.name;
    document.getElementById('edit-category').value = item.category || 'General';
    document.getElementById('edit-reorder').value = item.reorder_level_kg;
    document.getElementById('edit-stock').value = item.current_stock_kg;
    document.getElementById('edit-cost').value = item.average_cost_per_kg;

    document.getElementById('edit-modal').classList.add('active');
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('active');
}

async function handleUpdateItem(e) {
    e.preventDefault();
    clearStatus();

    const itemId = document.getElementById('edit-item-id').value;
    const name = document.getElementById('edit-name').value.trim();
    const category = document.getElementById('edit-category').value;
    const reorder = parseFloat(document.getElementById('edit-reorder').value);
    const stock = parseFloat(document.getElementById('edit-stock').value);
    const cost = parseFloat(document.getElementById('edit-cost').value);

    try {
        await apiRequest(`/api/feed/items/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({
                name,
                category,
                reorder_level_kg: reorder,
                current_stock_kg: stock,
                average_cost_per_kg: cost,
                updated_by: DEFAULT_USER
            })
        });

        closeEditModal();
        setStatus(`Ingredient "${name}" updated successfully!`);
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// DELETE INGREDIENT
// -----------------------------------------------------------------------------
async function handleDeleteItem(itemId, itemName) {
    if (!confirm(`Are you sure you want to delete feed ingredient "${itemName}"?\nThis will remove it from active inventory.`)) {
        return;
    }

    clearStatus();
    try {
        await apiRequest(`/api/feed/items/${itemId}`, {
            method: 'DELETE'
        });
        setStatus(`Feed ingredient "${itemName}" deleted successfully.`);
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleRestoreItem(itemId, itemName) {
    clearStatus();
    try {
        await apiRequest(`/api/feed/items/${itemId}/restore`, {
            method: 'POST'
        });
        setStatus(`Feed ingredient "${itemName}" restored successfully.`);
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// RECORD PURCHASE & LIVE PREVIEW
// -----------------------------------------------------------------------------
function updatePurchaseCostPreview() {
    const qtyVal = parseFloat(document.getElementById('purchase-quantity').value) || 0;
    const unit = document.getElementById('purchase-unit').value;
    const totalCost = parseFloat(document.getElementById('purchase-total-cost').value) || 0;
    const previewBox = document.getElementById('purchase-cost-preview');

    if (qtyVal <= 0 || totalCost <= 0) {
        previewBox.style.display = 'none';
        return;
    }

    let qtyKg = qtyVal;
    if (unit === 'MT') {
        qtyKg = qtyVal * 1000.0;
    } else if (unit === 'bags') {
        qtyKg = qtyVal * 50.0;
    }

    const costPerKg = totalCost / qtyKg;
    const costPerMT = costPerKg * 1000.0;

    document.getElementById('preview-kg-qty').textContent = `Total weight: ${qtyKg.toLocaleString()} kg (${(qtyKg / 1000).toFixed(3)} MT)`;
    document.getElementById('preview-cost-kg').textContent = `Unit Cost: $${costPerKg.toFixed(4)} / kg`;
    document.getElementById('preview-cost-mt').textContent = `$${costPerMT.toFixed(2)} / MT`;
    previewBox.style.display = 'block';
}

async function handleSavePurchase(e) {
    e.preventDefault();
    clearStatus();

    const itemId = parseInt(document.getElementById('purchase-item-id').value);
    const purchaseDate = document.getElementById('purchase-date').value;
    const quantity = parseFloat(document.getElementById('purchase-quantity').value);
    const unit = document.getElementById('purchase-unit').value;
    const totalCost = parseFloat(document.getElementById('purchase-total-cost').value);
    const vendorName = document.getElementById('purchase-vendor').value.trim();
    const invoiceNo = document.getElementById('purchase-invoice').value.trim();
    const remarks = document.getElementById('purchase-remarks').value.trim();

    if (!itemId || !purchaseDate || !quantity || !totalCost) {
        setStatus('Please fill in all mandatory purchase fields.', 'error');
        return;
    }

    try {
        await apiRequest('/api/feed/purchases', {
            method: 'POST',
            body: JSON.stringify({
                item_id: itemId,
                purchase_date: purchaseDate,
                quantity,
                unit,
                total_cost: totalCost,
                vendor_name: vendorName,
                invoice_no: invoiceNo,
                remarks,
                created_by: DEFAULT_USER
            })
        });

        setStatus('Feed purchase saved! Inventory stock and weighted average costs have been updated.');
        document.getElementById('purchase-form').reset();
        document.getElementById('purchase-cost-preview').style.display = 'none';
        setDefaultDate('purchase-date');
        await loadFeedInventory();
        switchTab('stock-tab');
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// PURCHASES HISTORY
// -----------------------------------------------------------------------------
async function loadPurchases() {
    clearStatus();
    const filterItem = document.getElementById('history-filter-item').value;
    const showArchived = document.getElementById('show-archived-purchases')?.checked;

    let url = '/api/feed/purchases?';
    const params = new URLSearchParams();
    if (filterItem) params.append('item_id', filterItem);
    if (showArchived) params.append('include_deleted', 'true');
    url += params.toString();

    try {
        allPurchases = await apiRequest(url);
        renderPurchasesTable(allPurchases);
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

function renderPurchasesTable(purchases) {
    const tbody = document.getElementById('purchase-table-body');
    if (!purchases || purchases.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #627d98;">No purchase records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = purchases.map(p => {
        const isDel = p.is_deleted;
        const actionHtml = isDel
            ? `<button type="button" class="btn-sm" style="background: #16a34a; color: white;" onclick="handleRestorePurchase(${p.purchase_id})">↩️ Restore</button>`
            : `<button type="button" class="btn-sm btn-danger" onclick="handleDeletePurchase(${p.purchase_id})">Delete</button>`;

        return `
            <tr style="${isDel ? 'opacity: 0.65; background: #fafafa;' : ''}">
                <td>${p.purchase_date}</td>
                <td>
                    <strong>${escapeHtml(p.item_name || `Item #${p.item_id}`)}</strong>
                    ${isDel ? '<span class="badge" style="background: #fee2e2; color: #991b1b; margin-left: 6px;">Deleted</span>' : ''}
                </td>
                <td><strong>${(p.quantity_mt || 0).toFixed(3)} MT</strong></td>
                <td>${(p.quantity_kg || 0).toLocaleString()} kg</td>
                <td>$${(p.cost_per_kg || 0).toFixed(4)}</td>
                <td>$${(p.cost_per_mt || 0).toFixed(2)}</td>
                <td><strong>$${(p.total_cost || 0).toFixed(2)}</strong></td>
                <td>${escapeHtml(p.vendor_name || '-')}</td>
                <td>${escapeHtml(p.invoice_no || '-')}</td>
                <td>${actionHtml}</td>
            </tr>
        `;
    }).join('');
}

async function handleDeletePurchase(purchaseId) {
    if (!confirm('Are you sure you want to delete this purchase record?\nThis will deduct the purchased quantity from available inventory stock.')) {
        return;
    }

    clearStatus();
    try {
        await apiRequest(`/api/feed/purchases/${purchaseId}`, {
            method: 'DELETE'
        });
        setStatus('Purchase record deleted and stock adjusted.');
        await loadPurchases();
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleRestorePurchase(purchaseId) {
    clearStatus();
    try {
        await apiRequest(`/api/feed/purchases/${purchaseId}/restore`, {
            method: 'POST'
        });
        setStatus('Purchase record restored and inventory stock re-added.');
        await loadPurchases();
        await loadFeedInventory();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate('purchase-date');
    loadFeedInventory();
});
