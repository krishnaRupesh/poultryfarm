const DIET_COLORS = [
    '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6', '#f97316'
];

function setAnalysisDate(dateStr) {
    document.getElementById('analysis-date').value = dateStr;
    loadDailyAnalysis();
}

async function loadDailyAnalysis() {
    clearStatus();
    const dateInput = document.getElementById('analysis-date');
    const batchSelect = document.getElementById('filter-batch-id');
    let selDate = dateInput.value;
    let selBatch = batchSelect ? batchSelect.value : '';

    let url = '/api/analysis/daily?';
    const params = new URLSearchParams();
    if (selDate) params.append('date', selDate);
    if (selBatch) params.append('batch_id', selBatch);
    url += params.toString();

    try {
        const data = await apiRequest(url);
        dateInput.value = data.date;

        renderDailyKPIs(data);
        renderBatchBreakdown(data.batch_breakdown);
        renderDietBreakdown(data.feed.items, data.feed.total_feed_cost);
        renderComparisonBox(data);

        // Load historical trends table
        loadHistory(14);
    } catch (err) {
        setStatus(`Error loading analysis: ${err.message}`, 'error');
        document.getElementById('analysis-status-pill').textContent = 'Error';
    }
}

function renderBatchBreakdown(breakdown) {
    const tbody = document.getElementById('batch-breakdown-body');
    if (!tbody) return;

    if (!breakdown || breakdown.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: #627d98;">No batch logs recorded for this date.</td></tr>';
        return;
    }

    tbody.innerHTML = breakdown.map(b => {
        const costEggDisplay = b.cost_per_egg > 0 ? `$${b.cost_per_egg.toFixed(4)}` : '$0.0000';
        return `
            <tr>
                <td><strong>${escapeHtml(b.batch_name)}</strong></td>
                <td><span class="badge" style="background: #e2e8f0; color: #102a43;">🛖 ${escapeHtml(b.shed_name)}</span></td>
                <td>${escapeHtml(b.breed || 'Layer')} (${b.age_weeks} wks)</td>
                <td><strong>${(b.active_birds || 0).toLocaleString()}</strong></td>
                <td>${b.mortality || 0}</td>
                <td>${(b.feed_kg || 0).toLocaleString()} kg (${((b.feed_kg || 0) / 1000).toFixed(3)} MT)</td>
                <td><strong>$${(b.feed_cost || 0).toFixed(2)}</strong></td>
                <td>$${(b.feed_cost_per_bird || 0).toFixed(4)}</td>
                <td>${(b.eggs_produced || 0).toLocaleString()}</td>
                <td><strong style="color: #0b69a3;">${(b.laying_percentage || 0).toFixed(1)}%</strong></td>
                <td style="color: #b7791f; font-weight: bold;">${costEggDisplay}</td>
            </tr>
        `;
    }).join('');
}

function renderDailyKPIs(data) {
    const flock = data.flock;
    const feed = data.feed;
    const prod = data.production;
    const sales = data.sales_and_stock;
    const prof = data.profitability;

    // Status Pill
    const pill = document.getElementById('analysis-status-pill');
    if (prof.is_profitable) {
        pill.textContent = `✅ Profitable (+${(prof.profit_margin_per_egg >= 0 ? '$' : '-$')}${Math.abs(prof.profit_margin_per_egg).toFixed(4)} / egg)`;
        pill.style.background = '#d1fae5';
        pill.style.color = '#065f46';
    } else if (prod.eggs_produced > 0) {
        pill.textContent = `⚠️ Loss Margin (${(prof.profit_margin_per_egg).toFixed(4)} / egg)`;
        pill.style.background = '#fee2e2';
        pill.style.color = '#991b1b';
    } else {
        pill.textContent = `No egg production logged for this date`;
        pill.style.background = '#e2e8f0';
        pill.style.color = '#486581';
    }

    // 1. Feed cost per bird
    document.getElementById('kpi-cost-per-bird').textContent = `$${feed.feed_cost_per_bird.toFixed(4)}`;
    document.getElementById('kpi-bird-sub').textContent = `${flock.active_birds.toLocaleString()} birds (${feed.feed_grams_per_bird}g feed/bird)`;

    // 2. Production cost per egg
    document.getElementById('kpi-cost-per-egg').textContent = `$${prod.production_cost_per_egg.toFixed(4)}`;
    document.getElementById('kpi-egg-cost-sub').textContent = prod.eggs_produced > 0
        ? `Feed: $${feed.total_feed_cost.toFixed(2)} ÷ ${prod.eggs_produced.toLocaleString()} eggs`
        : 'No eggs produced today';

    // 3. Today's egg price
    document.getElementById('kpi-egg-price').textContent = `$${sales.egg_selling_price.toFixed(4)}`;
    document.getElementById('kpi-price-sub').textContent = sales.egg_selling_price > 0 ? 'Today\'s selling rate' : 'No price set';

    // 4. Margin per egg
    const marginEl = document.getElementById('kpi-egg-margin');
    const isProf = prof.profit_margin_per_egg >= 0;
    marginEl.textContent = `${isProf ? '+' : ''}$${prof.profit_margin_per_egg.toFixed(4)}`;
    marginEl.style.color = isProf ? '#155724' : '#721c24';

    const marginPct = sales.egg_selling_price > 0
        ? ((prof.profit_margin_per_egg / sales.egg_selling_price) * 100).toFixed(1)
        : '0.0';
    document.getElementById('kpi-margin-sub').textContent = `${isProf ? '+' : ''}${marginPct}% margin on selling price`;

    // 5. Total feed cost
    document.getElementById('kpi-total-feed-cost').textContent = `$${feed.total_feed_cost.toFixed(2)}`;
    document.getElementById('kpi-feed-weight-sub').textContent = `${feed.total_feed_mt.toFixed(3)} MT (${feed.total_feed_kg.toLocaleString()} kg)`;

    // 6. Eggs produced
    document.getElementById('kpi-eggs-produced').textContent = prod.eggs_produced.toLocaleString();
    document.getElementById('kpi-laying-rate').textContent = `${prod.laying_percentage.toFixed(1)}% laying rate (flock)`;

    // 7. Eggs sold
    document.getElementById('kpi-eggs-sold').textContent = sales.eggs_sold.toLocaleString();
    document.getElementById('kpi-revenue-sub').textContent = `Revenue: $${sales.actual_revenue.toFixed(2)}`;

    // 8. Realized profit
    const profEl = document.getElementById('kpi-realized-profit');
    const isNetProf = prof.realized_gross_profit >= 0;
    profEl.textContent = `${isNetProf ? '+' : ''}$${prof.realized_gross_profit.toFixed(2)}`;
    profEl.style.color = isNetProf ? '#155724' : '#721c24';
    document.getElementById('kpi-unsold-stock-sub').textContent = `Unsold stock: ${sales.closing_stock.toLocaleString()} eggs`;
}

function renderComparisonBox(data) {
    const flock = data.flock;
    const feed = data.feed;
    const prod = data.production;
    const sales = data.sales_and_stock;
    const prof = data.profitability;

    // Production Left Box
    document.getElementById('comp-feed-spent').textContent = `$${feed.total_feed_cost.toFixed(2)}`;
    document.getElementById('comp-flock-count').textContent = `${flock.active_birds.toLocaleString()} birds`;
    document.getElementById('comp-feed-intake').textContent = `${feed.feed_grams_per_bird} grams / bird`;
    document.getElementById('comp-eggs-gathered').textContent = `${prod.eggs_produced.toLocaleString()} eggs`;
    document.getElementById('comp-egg-cost').textContent = `$${prod.production_cost_per_egg.toFixed(4)} / egg`;

    // Sales Right Box
    document.getElementById('comp-selling-price').textContent = `$${sales.egg_selling_price.toFixed(4)} / egg`;
    document.getElementById('comp-eggs-sold').textContent = `${sales.eggs_sold.toLocaleString()} eggs`;
    document.getElementById('comp-sales-pct').textContent = `${sales.sales_rate_pct}%`;
    document.getElementById('comp-revenue').textContent = `$${sales.actual_revenue.toFixed(2)}`;
    document.getElementById('comp-closing-eggs').textContent = `${sales.closing_stock.toLocaleString()} eggs`;
    document.getElementById('comp-unsold-val').textContent = `$${sales.unsold_inventory_value.toFixed(2)}`;

    const compProfEl = document.getElementById('comp-net-profit');
    const isNet = prof.realized_gross_profit >= 0;
    compProfEl.textContent = `${isNet ? '+' : ''}$${prof.realized_gross_profit.toFixed(2)}`;
    compProfEl.style.color = isNet ? '#046c4e' : '#9b1c1c';
}

function renderDietBreakdown(items, totalCost) {
    const tbody = document.getElementById('diet-breakdown-body');
    const track = document.getElementById('diet-progress-track');

    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #627d98;">No feed consumption recorded on this date.</td></tr>`;
        track.innerHTML = '';
        return;
    }

    // Build visual colored segments
    track.innerHTML = items.map((item, idx) => {
        const color = DIET_COLORS[idx % DIET_COLORS.length];
        return `<div class="progress-segment" style="width: ${item.pct_of_cost}%; background-color: ${color};" title="${escapeHtml(item.item_name)}: ${item.pct_of_cost}% cost"></div>`;
    }).join('');

    tbody.innerHTML = items.map((item, idx) => {
        const color = DIET_COLORS[idx % DIET_COLORS.length];
        return `
            <tr>
                <td>
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${color}; margin-right: 6px;"></span>
                    <strong>${escapeHtml(item.item_name)}</strong>
                </td>
                <td>${escapeHtml(item.category || 'General')}</td>
                <td><strong>${item.quantity_mt.toFixed(3)} MT</strong></td>
                <td>${item.quantity_kg.toLocaleString()} kg</td>
                <td>$${item.cost_per_kg.toFixed(4)}</td>
                <td>$${item.cost_per_mt.toFixed(2)}</td>
                <td><strong>$${item.total_cost.toFixed(2)}</strong></td>
                <td><span class="badge" style="background: #eef2ff; color: #3730a3;">${item.pct_of_cost}%</span></td>
                <td>${item.pct_of_weight}%</td>
                <td>${escapeHtml(item.remarks || '-')}</td>
            </tr>
        `;
    }).join('');
}

async function loadHistory(days = 14) {
    try {
        const historyData = await apiRequest(`/api/analysis/history?days=${days}`);
        renderHistoryTable(historyData);
    } catch (err) {
        document.getElementById('history-table-body').innerHTML = `<tr><td colspan="12" style="text-align: center; color: #dc3545;">Failed to load trends: ${err.message}</td></tr>`;
    }
}

function renderHistoryTable(records) {
    const tbody = document.getElementById('history-table-body');
    if (!records || records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="12" style="text-align: center; color: #627d98;">No multi-day history found.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.map(r => {
        const isProf = r.profitability.profit_margin_per_egg >= 0;
        const marginColor = isProf ? '#155724' : '#721c24';
        const profitColor = r.profitability.realized_gross_profit >= 0 ? '#155724' : '#721c24';

        return `
            <tr>
                <td>
                    <a href="javascript:void(0)" onclick="setAnalysisDate('${r.date}')" style="font-weight: bold; text-decoration: underline;">
                        ${r.date}
                    </a>
                </td>
                <td>${r.flock.active_birds.toLocaleString()}</td>
                <td><strong>${r.feed.total_feed_mt.toFixed(3)} MT</strong></td>
                <td>$${r.feed.total_feed_cost.toFixed(2)}</td>
                <td>$${r.feed.feed_cost_per_bird.toFixed(4)}</td>
                <td>${r.production.eggs_produced.toLocaleString()}</td>
                <td><strong>$${r.production.production_cost_per_egg.toFixed(4)}</strong></td>
                <td>$${r.sales_and_stock.egg_selling_price.toFixed(4)}</td>
                <td style="color: ${marginColor}; font-weight: bold;">
                    ${isProf ? '+' : ''}$${r.profitability.profit_margin_per_egg.toFixed(4)}
                </td>
                <td>${r.sales_and_stock.eggs_sold.toLocaleString()}</td>
                <td style="color: ${profitColor}; font-weight: bold;">
                    ${r.profitability.realized_gross_profit >= 0 ? '+' : ''}$${r.profitability.realized_gross_profit.toFixed(2)}
                </td>
                <td>${r.sales_and_stock.closing_stock.toLocaleString()} eggs</td>
            </tr>
        `;
    }).join('');
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

async function loadBatchOptions() {
    try {
        const batches = await apiRequest('/api/flock/batches');
        const batchSelect = document.getElementById('filter-batch-id');
        if (batchSelect && batches) {
            batches.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.batch_id;
                opt.textContent = `${b.batch_name} [${b.shed_name || 'No Shed'}]`;
                batchSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.warn('Could not load batches:', err);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadBatchOptions();

    // Check if date or batch_id is in query params
    const params = new URLSearchParams(window.location.search);
    const dateParam = params.get('date');
    const batchParam = params.get('batch_id');

    if (dateParam) {
        document.getElementById('analysis-date').value = dateParam;
    } else {
        document.getElementById('analysis-date').value = '2026-10-05';
    }

    if (batchParam) {
        const batchSelect = document.getElementById('filter-batch-id');
        if (batchSelect) batchSelect.value = batchParam;
    }

    await loadDailyAnalysis();
});
