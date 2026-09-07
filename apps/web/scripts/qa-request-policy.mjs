// Classify both observed request boundaries explicitly. A preview POST is not a
// book mutation; any confirm/create/settings/unknown POST is forbidden in QA.
export function isReadOnlyQaRequest(request, boundary) {
    if (['GET', 'HEAD', 'OPTIONS'].includes(request.method)) return true;
    if (request.method !== 'POST') return false;
    if (boundary === 'browser') {
        return (['/login', '/logout'].includes(request.path) && request.search === '')
            || (request.path === '/transactions/new' && request.search === '?/preview');
    }
    if (boundary === 'api') {
        return request.search === '' && (request.path === '/auth/login'
            || /^\/books\/[1-9]\d*\/transactions\/create-preview$/.test(request.path));
    }
    return false;
}
