let shedsList = [];
let batchesList = [];

async function loadAllData() {
    clearStatus();
    await loadSheds();
    await loadBatches();
    updateKpis();
}

async function loadSheds() {
    try {
        shedsList = await apiRequest('/api/flock/sheds');
        renderSheds();
        populateShedDropdown();
    } catch (err) {
        setStatus(`Failed to load sheds: ${err.message}`, 'error');
    }
}

async function loadBatches() {
    const showArchived = document.getElementById('show-archived-batches')?.checked;
    const url = showArchived ? '/api/flock/batches?include_deleted=true' : '/api/flock/batches';

    try {
        batchesList = await apiRequest(url);
        renderBatches();
        updateKpis();
    } catch (err) {
        setStatus(`Failed to load batches: ${err.message}`, 'error');
    }
}

function renderSheds() {
    const container = document.getElementById('sheds-container');
    if (!shedsList || shedsList.length === 0) {
        container.innerHTML = '<p style="color: #627d98;">No sheds configured yet. Click "+ Add New Shed" to get started.</p>';
        return;
    }

    container.innerHTML = shedsList.map(shed => {
        const isArchived = shed.is_deleted;
        const statusBadge = isArchived
            ? '<span class="badge badge-archived">Archived</span>'
            : (shed.status === 'Active'
                ? '<span class="badge badge-active">Active</span>'
                : `<span class="badge badge-warning">${shed.status}</span>`);

        const housedBatch = shed.active_batch_name
            ? `<div style="margin-top: 8px; font-size: 0.9rem;"><strong>Housed Batch:</strong> <span style="color: #0b69a3; font-weight: bold;">${escapeHtml(shed.active_batch_name)}</span> (${(shed.active_birds || 0).toLocaleString()} birds)</div>`
            : '<div style="margin-top: 8px; font-size: 0.9rem; color: #829ab1;"><em>No active batch assigned</em></div>';

        return `
            <div class="shed-card ${shed.status !== 'Active' ? 'inactive' : ''}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0 0 4px 0; font-size: 1.15rem; color: #102a43;">${escapeHtml(shed.shed_name)}</h3>
                        <span style="font-size: 0.8rem; color: #627d98;">${escapeHtml(shed.shed_type || 'Layer')} • ${escapeHtml(shed.location || 'Main Farm')}</span>
                    </div>
                    ${statusBadge}
                </div>

                <div style="margin-top: 12px; font-size: 0.9rem;">
                    <strong>Capacity:</strong> ${(shed.capacity || 0).toLocaleString()} birds
                </div>

                ${housedBatch}

                ${shed.description ? `<p style="font-size: 0.82rem; color: #627d98; margin: 8px 0 0 0;">${escapeHtml(shed.description)}</p>` : ''}

                <div style="margin-top: 14px; display: flex; gap: 8px; justify-content: flex-end; border-top: 1px solid #f0f4f8; padding-top: 10px;">
                    ${isArchived
                        ? `<button type="button" class="btn-sm" style="background: #10b981;" onclick="handleRestoreShed(${shed.shed_id})">↩️ Restore</button>`
                        : `<button type="button" class="btn-sm secondary" onclick="openEditShedModal(${shed.shed_id})">Edit</button>
                           <button type="button" class="btn-sm btn-danger" onclick="handleDeleteShed(${shed.shed_id}, '${escapeHtml(shed.shed_name)}')">Archive</button>`
                    }
                </div>
            </div>
        `;
    }).join('');
}

function renderBatches() {
    const tbody = document.getElementById('batches-table-body');
    if (!batchesList || batchesList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #627d98; padding: 20px;">No batches placed yet. Click "+ Place New Batch" to add your first flock lifecycle.</td></tr>';
        return;
    }

    tbody.innerHTML = batchesList.map(batch => {
        const isArchived = batch.is_deleted;
        const statusBadge = isArchived
            ? '<span class="badge badge-archived">Archived</span>'
            : (batch.status === 'Active'
                ? '<span class="badge badge-active">Active</span>'
                : `<span class="badge badge-warning">${batch.status}</span>`);

        return `
            <tr style="${isArchived ? 'opacity: 0.6; background: #f8fafc;' : ''}">
                <td>
                    <strong>${escapeHtml(batch.batch_name)}</strong>
                    ${batch.remarks ? `<div style="font-size: 0.75rem; color: #627d98;">${escapeHtml(batch.remarks)}</div>` : ''}
                </td>
                <td>${batch.shed_name ? `<span style="font-weight: bold; color: #1f6feb;">${escapeHtml(batch.shed_name)}</span>` : '<span style="color: #9fb3c8;">None</span>'}</td>
                <td>${escapeHtml(batch.breed || 'BV300')} <span style="font-size: 0.8rem; color: #627d98;">(${escapeHtml(batch.bird_type || 'Layer')})</span></td>
                <td>${batch.placement_date || '--'}</td>
                <td><strong style="color: #0b69a3;">${batch.age_weeks || '--'} wks</strong></td>
                <td>${(batch.initial_birds || 0).toLocaleString()}</td>
                <td><strong style="color: #155724;">${(batch.current_birds || 0).toLocaleString()}</strong></td>
                <td>
                    ${batch.mortality_count > 0
                        ? `<span style="color: #b7791f;">${batch.mortality_count.toLocaleString()} (${batch.mortality_pct}%)</span>`
                        : '<span style="color: #155724;">0 (0%)</span>'
                    }
                </td>
                <td>${statusBadge}</td>
                <td>
                    ${isArchived
                        ? `<button type="button" class="btn-sm" style="background: #10b981;" onclick="handleRestoreBatch(${batch.batch_id})">↩️ Restore</button>`
                        : `<button type="button" class="btn-sm secondary" onclick="openEditBatchModal(${batch.batch_id})">Edit</button>
                           <button type="button" class="btn-sm btn-danger" onclick="handleDeleteBatch(${batch.batch_id}, '${escapeHtml(batch.batch_name)}')">Archive</button>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

function updateKpis() {
    const activeSheds = shedsList.filter(s => !s.is_deleted && s.status === 'Active');
    const totalCap = activeSheds.reduce((acc, s) => acc + (s.capacity || 0), 0);

    const activeBatches = batchesList.filter(b => !b.is_deleted && b.status === 'Active');
    const totalBirds = activeBatches.reduce((acc, b) => acc + (b.current_birds || 0), 0);
    const initialBirds = activeBatches.reduce((acc, b) => acc + (b.initial_birds || 0), 0);
    const deadBirds = Math.max(0, initialBirds - totalBirds);
    const mortPct = initialBirds > 0 ? ((deadBirds / initialBirds) * 100).toFixed(1) : '0.0';

    document.getElementById('kpi-active-sheds').textContent = activeSheds.length;
    document.getElementById('kpi-total-capacity').textContent = `Total Capacity: ${totalCap.toLocaleString()} birds`;
    document.getElementById('kpi-active-batches').textContent = activeBatches.length;
    document.getElementById('kpi-total-birds').textContent = `${totalBirds.toLocaleString()} birds`;
    document.getElementById('kpi-mortality-rate').textContent = `${deadBirds.toLocaleString()} (${mortPct}%)`;
}

function populateShedDropdown() {
    const sel = document.getElementById('batch-shed-id');
    if (!sel) return;
    const activeSheds = shedsList.filter(s => !s.is_deleted);
    sel.innerHTML = activeSheds.map(s => `
        <option value="${s.shed_id}">${escapeHtml(s.shed_name)} (Cap: ${(s.capacity || 0).toLocaleString()})</option>
    `).join('');
}

// -----------------------------------------------------------------------------
// SHED MODAL HANDLERS
// -----------------------------------------------------------------------------
function openShedModal() {
    document.getElementById('shed-modal-title').textContent = 'Add New Shed';
    document.getElementById('shed-form').reset();
    document.getElementById('shed-id').value = '';
    document.getElementById('shed-modal').classList.add('active');
}

function openEditShedModal(shedId) {
    const shed = shedsList.find(s => s.shed_id === shedId);
    if (!shed) return;

    document.getElementById('shed-modal-title').textContent = `Edit ${shed.shed_name}`;
    document.getElementById('shed-id').value = shed.shed_id;
    document.getElementById('shed-name').value = shed.shed_name;
    document.getElementById('shed-capacity').value = shed.capacity;
    document.getElementById('shed-type').value = shed.shed_type || 'Layer';
    document.getElementById('shed-status').value = shed.status || 'Active';
    document.getElementById('shed-location').value = shed.location || '';
    document.getElementById('shed-description').value = shed.description || '';

    document.getElementById('shed-modal').classList.add('active');
}

function closeShedModal() {
    document.getElementById('shed-modal').classList.remove('active');
}

async function handleSaveShed(e) {
    e.preventDefault();
    clearStatus();

    const shedId = document.getElementById('shed-id').value;
    const payload = {
        shed_name: document.getElementById('shed-name').value.trim(),
        capacity: parseInt(document.getElementById('shed-capacity').value),
        shed_type: document.getElementById('shed-type').value,
        status: document.getElementById('shed-status').value,
        location: document.getElementById('shed-location').value.trim() || null,
        description: document.getElementById('shed-description').value.trim() || null,
        created_by: DEFAULT_USER,
        updated_by: DEFAULT_USER
    };

    try {
        if (shedId) {
            await apiRequest(`/api/flock/sheds/${shedId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            setStatus(`Shed "${payload.shed_name}" updated successfully.`);
        } else {
            await apiRequest('/api/flock/sheds', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            setStatus(`Shed "${payload.shed_name}" created successfully.`);
        }
        closeShedModal();
        await loadSheds();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleDeleteShed(shedId, name) {
    if (!confirm(`Are you sure you want to archive shed "${name}"?\nAny assigned batches will remain accessible in history.`)) return;
    clearStatus();
    try {
        await apiRequest(`/api/flock/sheds/${shedId}?deleted_by=${DEFAULT_USER}`, { method: 'DELETE' });
        setStatus(`Shed "${name}" archived successfully.`);
        await loadSheds();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleRestoreShed(shedId) {
    clearStatus();
    try {
        await apiRequest(`/api/flock/sheds/${shedId}/restore`, { method: 'POST' });
        setStatus('Shed restored successfully.');
        await loadSheds();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// BATCH MODAL HANDLERS
// -----------------------------------------------------------------------------
function openBatchModal() {
    document.getElementById('batch-modal-title').textContent = 'Place New Flock Batch';
    document.getElementById('batch-form').reset();
    document.getElementById('batch-id').value = '';
    document.getElementById('batch-placement-date').value = today();
    document.getElementById('batch-initial-age').value = 18;
    populateShedDropdown();
    document.getElementById('batch-modal').classList.add('active');
}

function openEditBatchModal(batchId) {
    const batch = batchesList.find(b => b.batch_id === batchId);
    if (!batch) return;

    document.getElementById('batch-modal-title').textContent = `Edit Batch ${batch.batch_name}`;
    document.getElementById('batch-id').value = batch.batch_id;
    document.getElementById('batch-name').value = batch.batch_name;
    document.getElementById('batch-shed-id').value = batch.shed_id || '';
    document.getElementById('batch-breed').value = batch.breed;
    document.getElementById('batch-bird-type').value = batch.bird_type || 'Layer';
    document.getElementById('batch-placement-date').value = batch.placement_date;
    document.getElementById('batch-initial-age').value = batch.initial_age_weeks || 18;
    document.getElementById('batch-initial-birds').value = batch.initial_birds;
    document.getElementById('batch-current-birds').value = batch.current_birds;
    document.getElementById('batch-status').value = batch.status || 'Active';
    document.getElementById('batch-depletion-date').value = batch.depletion_date || '';
    document.getElementById('batch-remarks').value = batch.remarks || '';

    document.getElementById('batch-modal').classList.add('active');
}

function closeBatchModal() {
    document.getElementById('batch-modal').classList.remove('active');
}

function syncCurrentBirds() {
    const init = document.getElementById('batch-initial-birds').value;
    const curr = document.getElementById('batch-current-birds');
    if (!document.getElementById('batch-id').value && init) {
        curr.value = init;
    }
}

async function handleSaveBatch(e) {
    e.preventDefault();
    clearStatus();

    const batchId = document.getElementById('batch-id').value;
    const payload = {
        batch_name: document.getElementById('batch-name').value.trim(),
        shed_id: parseInt(document.getElementById('batch-shed-id').value) || null,
        breed: document.getElementById('batch-breed').value.trim(),
        bird_type: document.getElementById('batch-bird-type').value,
        placement_date: document.getElementById('batch-placement-date').value,
        initial_age_weeks: parseInt(document.getElementById('batch-initial-age').value) || 18,
        initial_birds: parseInt(document.getElementById('batch-initial-birds').value),
        current_birds: parseInt(document.getElementById('batch-current-birds').value),
        status: document.getElementById('batch-status').value,
        depletion_date: document.getElementById('batch-depletion-date').value || null,
        remarks: document.getElementById('batch-remarks').value.trim() || null,
        created_by: DEFAULT_USER,
        updated_by: DEFAULT_USER
    };

    try {
        if (batchId) {
            await apiRequest(`/api/flock/batches/${batchId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            setStatus(`Flock batch "${payload.batch_name}" updated.`);
        } else {
            await apiRequest('/api/flock/batches', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            setStatus(`Flock batch "${payload.batch_name}" created and placed into shed.`);
        }
        closeBatchModal();
        await loadBatches();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleDeleteBatch(batchId, name) {
    if (!confirm(`Are you sure you want to archive batch "${name}"?\nHistoric feeding and egg records will be preserved.`)) return;
    clearStatus();
    try {
        await apiRequest(`/api/flock/batches/${batchId}?deleted_by=${DEFAULT_USER}`, { method: 'DELETE' });
        setStatus(`Batch "${name}" archived successfully.`);
        await loadBatches();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleRestoreBatch(batchId) {
    clearStatus();
    try {
        await apiRequest(`/api/flock/batches/${batchId}/restore`, { method: 'POST' });
        setStatus('Batch restored successfully.');
        await loadBatches();
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

document.addEventListener('DOMContentLoaded', loadAllData);
