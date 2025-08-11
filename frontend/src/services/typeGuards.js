// Type guards for API responses
// These perform minimal shape checks and return boolean

/**
 * Check if object is a DiscoveryResponse
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isDiscoveryResponse(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    Array.isArray(obj.matches) &&
    Array.isArray(obj.proposals) &&
    typeof obj.using_fallback === 'boolean' &&
    typeof obj.ranking_method === 'string' &&
    typeof obj.total_matches === 'number' &&
    typeof obj.total_proposals === 'number'
  );
}

/**
 * Check if object is an ActivationResponse
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isActivationResponse(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.activation_id === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.message === 'string' &&
    Array.isArray(obj.allowed_platforms) &&
    typeof obj.estimated_duration_minutes === 'number'
  );
}

/**
 * Check if object is a StatusResponse
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isStatusResponse(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.activation_id === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.details === 'object' &&
    typeof obj.created_at === 'string' &&
    typeof obj.updated_at === 'string'
  );
}

/**
 * Check if object is a HealthResponse
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isHealthResponse(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.ok === 'boolean' &&
    typeof obj.mode === 'string' &&
    typeof obj.timestamp === 'string' &&
    typeof obj.version === 'string'
  );
}

/**
 * Check if object is a SignalMatch
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isSignalMatch(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.data_provider === 'string' &&
    typeof obj.coverage_percentage === 'number' &&
    typeof obj.base_cpm === 'number' &&
    Array.isArray(obj.allowed_platforms) &&
    typeof obj.description === 'string'
  );
}

/**
 * Check if object is a Proposal
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isProposal(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    Array.isArray(obj.signal_ids) &&
    typeof obj.logic === 'string' &&
    Array.isArray(obj.platforms) &&
    typeof obj.description === 'string'
  );
}

/**
 * Check if object is an error response
 * @param {any} obj - Object to check
 * @returns {boolean}
 */
export function isErrorResponse(obj) {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.error === 'string' &&
    typeof obj.message === 'string'
  );
}
