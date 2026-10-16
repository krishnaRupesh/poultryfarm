const DEFAULT_USER = 'frontend';

// Supports standalone Cloud Storage hosting (via window.API_BASE_URL)
// or unified Cloud Run container hosting (relative path)
function getApiUrl(path) {
    const base = (typeof window !== 'undefined' && window.API_BASE_URL) ? window.API_BASE_URL.replace(/\/+$/, '') : '';
    if (base && path.startsWith('/')) {
        return `${base}${path}`;
    }
    return path;
}

async function apiRequest(path, options = {}) {
    const url = getApiUrl(path);
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        },
        ...options
    });

    const text = await response.text();
    let data = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch (error) {
        data = { error: text ? 'Server returned a non-JSON response. Check the Flask console.' : null };
    }

    if (!response.ok) {
        const message = data?.error || data?.message || `Request failed with status ${response.status}`;
        throw new Error(message);
    }

    return data;
}

function setStatus(message, type = 'success') {
    let status = document.getElementById('status-message');
    if (!status) {
        status = document.createElement('div');
        status.id = 'status-message';
        document.body.insertBefore(status, document.body.children[1] || null);
    }
    status.className = `status ${type}`;
    status.textContent = message;
}

function clearStatus() {
    const status = document.getElementById('status-message');
    if (status) {
        status.className = 'status';
        status.textContent = '';
    }
}

function money(value) {
    const amount = Number(value || 0);
    return amount.toFixed(2);
}

function today() {
    return new Date().toISOString().slice(0, 10);
}

function formPayload(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function setDefaultDate(id) {
    const field = document.getElementById(id);
    if (field && !field.value) {
        field.value = today();
    }
}

function populateSelect(select, items, getValue, getLabel, placeholder) {
    select.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach((item) => {
        const option = document.createElement('option');
        option.value = getValue(item);
        option.textContent = getLabel(item);
        select.appendChild(option);
    });
}
