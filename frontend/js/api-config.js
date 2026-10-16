// API Configuration for Poultry Farm Management
// In Unified Cloud Run: window.API_BASE_URL is empty ('') and requests use relative /api paths.
// In Standalone Cloud Storage: window.API_BASE_URL points to the deployed Cloud Run HTTPS service URL.
if (typeof window !== 'undefined' && !window.API_BASE_URL) {
    window.API_BASE_URL = '';
}
