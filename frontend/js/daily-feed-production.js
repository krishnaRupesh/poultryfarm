let feedInventory = [];
let feedRowIndex = 0;
let allBatches = [];
let allSheds = [];

function setTodayDate() {
    document.getElementById('operation-date').value = today();
    loadDateData();
}

async function loadFeedInventoryMaster() {
    try {
        const [items, sheds, batches] = await Promise.all([
            apiRequest('/api/feed/items'),
            apiRequest('/api/flock/sheds'),
            apiRequest('/api/flock/batches')
        ]);
        feedInventory = items;
        allSheds = sheds || [];
        allBatches = batches || [];

        const batchSelect = document.getElementById('flock-batch-id');
        if (batchSelect && batchSelect.options.length <= 1) {
            batches.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.batch_id;
                opt.textContent = `${b.batch_name} [${b.shed_name || 'No Shed'}] (${b.current_birds || 0} birds, ${b.age_weeks} wks)`;
                batchSelect.appendChild(opt);
            });
        }

        const shedSelect = document.getElementById('flock-shed-id');
        if (shedSelect && shedSelect.options.length <= 1) {
            sheds.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.shed_id;
                opt.textContent = `${s.shed_name} (${s.shed_type || 'General'})`;
                shedSelect.appendChild(opt);
            });
        }
    } catch (err) {
        setStatus(`Could not load masters: ${err.message}`, 'error');
    }
}

function handleBatchSelectionChange() {
    const batchId = parseInt(document.getElementById('flock-batch-id').value);
    if (!batchId) {
        loadDateData();
        return;
    }
    const batch = allBatches.find(b => b.batch_id === batchId);
    if (batch) {
        if (batch.shed_id) {
            document.getElementById('flock-shed-id').value = batch.shed_id;
        }
        if (batch.current_birds > 0) {
            document.getElementById('active-birds').value = batch.current_birds;
        }
    }
    loadDateData();
}

async function loadDateData() {
    clearStatus();
    const selDate = document.getElementById('operation-date').value;
    if (!selDate) return;

    const selBatch = document.getElementById('flock-batch-id')?.value;
    const batchQueryParam = selBatch ? `&batch_id=${selBatch}` : '';

    document.getElementById('view-analysis-link').href = `daily-cost-analysis.html?date=${selDate}${selBatch ? `&batch_id=${selBatch}` : ''}`;

    try {
        // 1. Fetch flock status for this date
        const flock = await apiRequest(`/api/daily/flock?date=${selDate}${batchQueryParam}`);
        if (flock && flock.active_birds > 0) {
            document.getElementById('active-birds').value = flock.active_birds;
            document.getElementById('flock-mortality').value = flock.mortality || 0;
            document.getElementById('flock-remarks').value = flock.remarks || '';
            if (flock.shed_id) document.getElementById('flock-shed-id').value = flock.shed_id;
        } else {
            // Check if batch has current birds
            const batchObj = selBatch ? allBatches.find(b => b.batch_id === parseInt(selBatch)) : null;
            document.getElementById('active-birds').value = batchObj ? batchObj.current_birds : 10000;
            document.getElementById('flock-mortality').value = 0;
            document.getElementById('flock-remarks').value = '';
        }

        // 2. Fetch feed consumption for this date
        const consumptions = await apiRequest(`/api/daily/consumption?date=${selDate}${batchQueryParam}`);
        const tbody = document.getElementById('feed-rows-body');
        tbody.innerHTML = '';
        feedRowIndex = 0;

        if (consumptions && consumptions.length > 0) {
            consumptions.forEach(c => {
                // Determine display unit: if >= 1000 and multiple of 1000, MT, else kg
                let unit = 'kg';
                let qty = c.quantity_kg;
                if (c.quantity_kg >= 1000 && c.quantity_kg % 100 === 0) {
                    unit = 'MT';
                    qty = c.quantity_kg / 1000.0;
                }
                addFeedRow(c.item_id, qty, unit, c.remarks);
            });
        } else {
            // Default 1 row for quick entry (e.g. Corn)
            const corn = feedInventory.find(i => i.name.toLowerCase().includes('corn'));
            addFeedRow(corn ? corn.item_id : (feedInventory[0]?.item_id || ''), 1, 'MT');
        }

        // 3. Fetch egg operations for this date
        const eggOps = await apiRequest(`/api/daily/egg-operations?date=${selDate}`);
        if (eggOps && eggOps.length > 0) {
            const op = eggOps[0];
            document.getElementById('opening-stock').value = op.opening_stock || 0;
            document.getElementById('eggs-produced').value = op.eggs_produced || 0;
            document.getElementById('damaged-eggs').value = op.damaged_eggs || 0;
            document.getElementById('eggs-sold').value = op.eggs_sold || 0;
            document.getElementById('egg-price').value = op.egg_price_per_unit || 0.075;
            document.getElementById('egg-price-unit').value = 'per_egg';
            document.getElementById('egg-remarks').value = op.remarks || '';
        } else {
            // Fetch previous closing stock to prefill opening stock
            const stockInfo = await apiRequest(`/api/daily/egg-operations/latest-stock?date=${selDate}`);
            document.getElementById('opening-stock').value = stockInfo.closing_stock || 0;
            document.getElementById('eggs-produced').value = '';
            document.getElementById('damaged-eggs').value = 0;
            document.getElementById('eggs-sold').value = '';
            document.getElementById('egg-price').value = '0.075';
            document.getElementById('egg-price-unit').value = 'per_egg';
            document.getElementById('egg-remarks').value = '';
        }

        calculateEggStock();
        calculateLiveMetrics();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// DYNAMIC FEED ROWS
// -----------------------------------------------------------------------------
function addFeedRow(selectedItemId = '', qty = '', unit = 'kg', remarks = '') {
    feedRowIndex++;
    const tbody = document.getElementById('feed-rows-body');
    const tr = document.createElement('tr');
    tr.id = `feed-row-${feedRowIndex}`;

    const options = feedInventory.map(i => {
        const sel = String(i.item_id) === String(selectedItemId) ? 'selected' : '';
        return `<option value="${i.item_id}" data-cost="${i.average_cost_per_kg || 0}" ${sel}>${escapeHtml(i.name)} ($${(i.average_cost_per_kg || 0).toFixed(4)}/kg)</option>`;
    }).join('');

    tr.innerHTML = `
        <td>
            <select class="feed-item-select" onchange="calculateRowCost(${feedRowIndex})" required>
                <option value="">Select ingredient...</option>
                ${options}
            </select>
        </td>
        <td>
            <input type="number" step="0.001" class="feed-qty-input" value="${qty}" required placeholder="Qty" oninput="calculateRowCost(${feedRowIndex})">
        </td>
        <td>
            <select class="feed-unit-select" onchange="calculateRowCost(${feedRowIndex})">
                <option value="MT" ${unit === 'MT' ? 'selected' : ''}>Metric Tons (MT)</option>
                <option value="kg" ${unit === 'kg' ? 'selected' : ''}>Kilograms (kg)</option>
                <option value="bags" ${unit === 'bags' ? 'selected' : ''}>Bags (50 kg)</option>
            </select>
        </td>
        <td>
            <span class="row-cost-display" style="font-weight: bold; color: #0b69a3;">$0.00</span>
        </td>
        <td>
            <button type="button" class="btn-sm btn-danger" onclick="removeFeedRow(${feedRowIndex})">Remove</button>
        </td>
    `;

    tbody.appendChild(tr);
    calculateRowCost(feedRowIndex);
}

function removeFeedRow(index) {
    const row = document.getElementById(`feed-row-${index}`);
    if (row) {
        row.remove();
        calculateTotalFeed();
        calculateLiveMetrics();
    }
}

function calculateRowCost(index) {
    const row = document.getElementById(`feed-row-${index}`);
    if (!row) return;

    const select = row.querySelector('.feed-item-select');
    const qtyInput = row.querySelector('.feed-qty-input');
    const unitSelect = row.querySelector('.feed-unit-select');
    const costDisplay = row.querySelector('.row-cost-display');

    const selectedOption = select.options[select.selectedIndex];
    const costPerKg = parseFloat(selectedOption?.getAttribute('data-cost')) || 0;
    const qtyVal = parseFloat(qtyInput.value) || 0;
    const unit = unitSelect.value;

    let qtyKg = qtyVal;
    if (unit === 'MT') {
        qtyKg = qtyVal * 1000.0;
    } else if (unit === 'bags') {
        qtyKg = qtyVal * 50.0;
    }

    const rowCost = qtyKg * costPerKg;
    costDisplay.textContent = `$${rowCost.toFixed(2)}`;
    row.dataset.kg = qtyKg;
    row.dataset.cost = rowCost;

    calculateTotalFeed();
    calculateLiveMetrics();
}

function calculateTotalFeed() {
    let totalKg = 0;
    let totalCost = 0;

    document.querySelectorAll('#feed-rows-body tr').forEach(row => {
        totalKg += parseFloat(row.dataset.kg) || 0;
        totalCost += parseFloat(row.dataset.cost) || 0;
    });

    const totalMT = (totalKg / 1000.0).toFixed(3);
    document.getElementById('total-feed-weight-display').textContent = `${totalMT} MT (${totalKg.toLocaleString()} kg)`;
    document.getElementById('total-feed-cost-display').textContent = `$${totalCost.toFixed(2)}`;

    return { totalKg, totalCost };
}

// -----------------------------------------------------------------------------
// EGG OPERATIONS STOCK CALCULATION
// -----------------------------------------------------------------------------
function calculateEggStock() {
    const opening = parseInt(document.getElementById('opening-stock').value) || 0;
    const produced = parseInt(document.getElementById('eggs-produced').value) || 0;
    const damaged = parseInt(document.getElementById('damaged-eggs').value) || 0;
    const sold = parseInt(document.getElementById('eggs-sold').value) || 0;

    const available = Math.max(0, opening + produced - damaged);
    const closing = available - sold;

    document.getElementById('display-eggs-available').textContent = `${available.toLocaleString()} eggs`;
    document.getElementById('display-closing-stock').textContent = `${closing.toLocaleString()} eggs`;

    // Calculate unit price per egg
    const rawPrice = parseFloat(document.getElementById('egg-price').value) || 0;
    const unitType = document.getElementById('egg-price-unit').value;
    let pricePerEgg = rawPrice;

    if (unitType === 'per_tray') {
        pricePerEgg = rawPrice / 30.0;
    } else if (unitType === 'per_hundred') {
        pricePerEgg = rawPrice / 100.0;
    } else if (unitType === 'per_dozen') {
        pricePerEgg = rawPrice / 12.0;
    }

    const revenue = sold * pricePerEgg;
    document.getElementById('display-unit-price').textContent = `$${pricePerEgg.toFixed(4)} / egg`;
    document.getElementById('display-actual-revenue').textContent = `$${revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    return { opening, produced, damaged, available, sold, closing, pricePerEgg, revenue };
}

function quickFillAllSold() {
    const opening = parseInt(document.getElementById('opening-stock').value) || 0;
    const produced = parseInt(document.getElementById('eggs-produced').value) || 0;
    const damaged = parseInt(document.getElementById('damaged-eggs').value) || 0;
    const available = Math.max(0, opening + produced - damaged);

    document.getElementById('eggs-sold').value = available;
    calculateEggStock();
    calculateLiveMetrics();
}

// -----------------------------------------------------------------------------
// LIVE METRIC CALCULATION PREVIEW
// -----------------------------------------------------------------------------
function calculateLiveMetrics() {
    const activeBirds = parseInt(document.getElementById('active-birds').value) || 0;
    const { totalCost } = calculateTotalFeed();
    const { produced, sold, pricePerEgg } = calculateEggStock();

    // 1. Cost per bird
    const costPerBird = activeBirds > 0 ? (totalCost / activeBirds) : 0;
    document.getElementById('preview-cost-per-bird').textContent = `$${costPerBird.toFixed(4)}`;

    // 2. Cost to produce 1 egg
    const costPerEgg = produced > 0 ? (totalCost / produced) : 0;
    document.getElementById('preview-cost-per-egg').textContent = `$${costPerEgg.toFixed(4)}`;

    // 3. Margin per egg sold
    const marginPerEgg = pricePerEgg - costPerEgg;
    const marginEl = document.getElementById('preview-margin-per-egg');
    marginEl.textContent = `${marginPerEgg >= 0 ? '+' : ''}$${marginPerEgg.toFixed(4)}`;
    marginEl.style.color = marginPerEgg >= 0 ? '#155724' : '#721c24';

    // 4. Realized gross profit
    const profit = sold * marginPerEgg;
    const profitEl = document.getElementById('preview-realized-profit');
    profitEl.textContent = `${profit >= 0 ? '+' : ''}$${profit.toFixed(2)}`;
    profitEl.style.color = profit >= 0 ? '#155724' : '#721c24';
}

// -----------------------------------------------------------------------------
// FORM SUBMISSION (FLOCK + FEED + EGG OPS)
// -----------------------------------------------------------------------------
async function handleSaveDailyOps(e) {
    e.preventDefault();
    clearStatus();

    const dateVal = document.getElementById('operation-date').value;
    const activeBirds = parseInt(document.getElementById('active-birds').value);
    const mortality = parseInt(document.getElementById('flock-mortality').value) || 0;
    const flockRemarks = document.getElementById('flock-remarks').value.trim();

    if (!dateVal || !activeBirds) {
        setStatus('Date and Active Birds count are mandatory.', 'error');
        return;
    }

    // Collect feed items
    const feedRows = document.querySelectorAll('#feed-rows-body tr');
    const feedItemsToPost = [];

    for (const row of feedRows) {
        const itemSelect = row.querySelector('.feed-item-select');
        const qtyInput = row.querySelector('.feed-qty-input');
        const unitSelect = row.querySelector('.feed-unit-select');

        const itemId = parseInt(itemSelect.value);
        const qty = parseFloat(qtyInput.value);
        const unit = unitSelect.value;

        if (itemId && qty > 0) {
            feedItemsToPost.push({
                item_id: itemId,
                quantity: qty,
                unit: unit,
            });
        }
    }

    // Collect egg ops
    const openingStock = parseInt(document.getElementById('opening-stock').value) || 0;
    const eggsProduced = parseInt(document.getElementById('eggs-produced').value);
    const damagedEggs = parseInt(document.getElementById('damaged-eggs').value) || 0;
    const eggsSold = parseInt(document.getElementById('eggs-sold').value);
    const eggPrice = parseFloat(document.getElementById('egg-price').value);
    const priceUnit = document.getElementById('egg-price-unit').value;
    const eggRemarks = document.getElementById('egg-remarks').value.trim();

    if (isNaN(eggsProduced) || isNaN(eggsSold) || isNaN(eggPrice)) {
        setStatus('Please complete all mandatory egg production and sales fields.', 'error');
        return;
    }

    const batchVal = document.getElementById('flock-batch-id')?.value;
    const shedVal = document.getElementById('flock-shed-id')?.value;
    const batchId = batchVal ? parseInt(batchVal) : null;
    const shedId = shedVal ? parseInt(shedVal) : null;

    try {
        // 1. Save flock count
        await apiRequest('/api/daily/flock', {
            method: 'POST',
            body: JSON.stringify({
                date: dateVal,
                active_birds: activeBirds,
                mortality: mortality,
                batch_id: batchId,
                shed_id: shedId,
                remarks: flockRemarks,
                created_by: DEFAULT_USER
            })
        });

        // 2. Save feed consumption items (if any specified)
        if (feedItemsToPost.length > 0) {
            await apiRequest('/api/daily/consumption', {
                method: 'POST',
                body: JSON.stringify({
                    date: dateVal,
                    batch_id: batchId,
                    shed_id: shedId,
                    items: feedItemsToPost,
                    created_by: DEFAULT_USER
                })
            });
        }

        // 3. Save egg operations
        await apiRequest('/api/daily/egg-operations', {
            method: 'POST',
            body: JSON.stringify({
                date: dateVal,
                opening_stock: openingStock,
                eggs_produced: eggsProduced,
                damaged_eggs: damagedEggs,
                eggs_sold: eggsSold,
                egg_price_per_unit: eggPrice,
                price_unit: priceUnit,
                batch_id: batchId,
                shed_id: shedId,
                remarks: eggRemarks,
                created_by: DEFAULT_USER
            })
        });

        setStatus(`Daily operations for ${dateVal} successfully recorded! Inventory stock adjusted.`);
        // Reload fresh data and update preview
        await loadFeedInventoryMaster();
        await loadDateData();
    } catch (err) {
        setStatus(`Failed to save operations: ${err.message}`, 'error');
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

document.addEventListener('DOMContentLoaded', async () => {
    setDefaultDate('operation-date');
    await loadFeedInventoryMaster();
    await loadDateData();
});
