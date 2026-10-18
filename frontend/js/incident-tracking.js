let allSheds = [];
let allBatches = [];

async function loadFilterOptions() {
    try {
        const [sheds, batches] = await Promise.all([
            apiRequest('/api/flock/sheds'),
            apiRequest('/api/flock/batches')
        ]);
        allSheds = sheds || [];
        allBatches = batches || [];

        const shedSelect = document.getElementById('filter-shed');
        sheds.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.shed_id;
            opt.textContent = s.shed_name;
            shedSelect.appendChild(opt);
        });

        const batchSelect = document.getElementById('filter-batch');
        batches.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.batch_id;
            opt.textContent = b.batch_name;
            batchSelect.appendChild(opt);
        });
    } catch (err) {
        console.warn('Could not load filters:', err);
    }
}

async function loadIncidents() {
    clearStatus();
    const tbody = document.getElementById('incident-list');
    const shedId = document.getElementById('filter-shed')?.value;
    const batchId = document.getElementById('filter-batch')?.value;
    const showArchived = document.getElementById('show-archived')?.checked;

    let url = '/api/incidents/?';
    const params = new URLSearchParams();
    if (shedId) params.append('shed_id', shedId);
    if (batchId) params.append('batch_id', batchId);
    if (showArchived) params.append('include_deleted', 'true');
    url += params.toString();

    try {
        const incidents = await apiRequest(url);
        if (!incidents || incidents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #627d98;">No incidents found.</td></tr>';
            return;
        }

        tbody.innerHTML = incidents.map((incident) => {
            const isDel = incident.is_deleted;
            const shedDisplay = incident.shed_name
                ? `<span class="badge" style="background: #e2e8f0; color: #102a43;">🛖 ${escapeHtml(incident.shed_name)}</span>`
                : '<span style="color: #829ab1; font-size: 0.85rem;">General Farm</span>';
            const batchDisplay = incident.batch_name
                ? `<span class="badge" style="background: #e0f2fe; color: #0369a1;">🐔 ${escapeHtml(incident.batch_name)}</span>`
                : '<span style="color: #829ab1; font-size: 0.85rem;">-</span>';

            const statusBadge = isDel
                ? '<span class="badge" style="background: #fee2e2; color: #991b1b;">Deleted</span>'
                : '<span class="badge" style="background: #dcfce7; color: #166534;">Active</span>';

            const actionButtons = isDel
                ? `<button class="btn-sm" style="background: #16a34a; color: white;" onclick="handleRestoreIncident('${incident.incident_id}')">↩️ Restore</button>`
                : `
                    <button class="btn-sm" onclick="redirectToUpdate('${incident.incident_id}')">Update</button>
                    <button class="btn-sm btn-danger" onclick="handleDeleteIncident('${incident.incident_id}', '${escapeHtml(incident.name)}')">Delete</button>
                  `;

            return `
                <tr style="${isDel ? 'opacity: 0.65; background: #fafafa;' : ''}">
                    <td><strong>${escapeHtml(incident.name)}</strong></td>
                    <td><span style="text-transform: capitalize;">${escapeHtml(incident.incident_type)}</span></td>
                    <td>${shedDisplay}</td>
                    <td>${batchDisplay}</td>
                    <td>${incident.incident_date}</td>
                    <td>${escapeHtml(incident.summary || '-')}</td>
                    <td>${money(incident.amount_spent)}</td>
                    <td>${statusBadge}</td>
                    <td>${actionButtons}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        setStatus(error.message, 'error');
    }
}

function redirectToUpdate(incidentId) {
    window.location.href = `incident-update.html?id=${incidentId}`;
}

async function handleDeleteIncident(incidentId, name) {
    if (!confirm(`Are you sure you want to delete incident "${name}"?\nThis record will be moved to the soft-delete archive.`)) {
        return;
    }
    clearStatus();
    try {
        await apiRequest(`/api/incidents/${incidentId}`, { method: 'DELETE' });
        setStatus(`Incident "${name}" archived successfully.`);
        await loadIncidents();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function handleRestoreIncident(incidentId) {
    clearStatus();
    try {
        await apiRequest(`/api/incidents/${incidentId}/restore`, { method: 'POST' });
        setStatus('Incident restored successfully.');
        await loadIncidents();
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

document.addEventListener('DOMContentLoaded', async () => {
    await loadFilterOptions();
    await loadIncidents();
});
