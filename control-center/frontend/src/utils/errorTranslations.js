/**
 * User-friendly error message translations
 * Converts technical error codes and messages into readable descriptions
 */

export const translateErrorMessage = (error) => {
  // Handle Axios errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Status code translations
    const statusMessages = {
      400: 'Invalid request. Please check your input and try again.',
      401: 'You are not authorized. Please log in again.',
      403: 'Access denied. You do not have permission to perform this action.',
      404: 'Service not found. It may have been removed or is unavailable.',
      422: 'Service configuration is invalid. Please check the service settings.',
      429: 'Too many requests. Please wait a moment and try again.',
      500: 'Service error. The backend service encountered an issue.',
      502: 'Gateway error. Unable to reach the service.',
      503: 'Service unavailable. The service is temporarily down for maintenance.',
      504: 'Request timeout. The service took too long to respond.',
    };

    // Check for specific error detail in response
    if (data?.detail) {
      // Map common backend error messages
      const detailLower = data.detail.toLowerCase();

      if (detailLower.includes('not found')) {
        return 'The requested resource could not be found.';
      }
      if (detailLower.includes('already exists')) {
        return 'This item already exists. Please use a different name.';
      }
      if (detailLower.includes('invalid') || detailLower.includes('validation')) {
        return 'Invalid input provided. Please check your data and try again.';
      }
      if (detailLower.includes('permission') || detailLower.includes('unauthorized')) {
        return 'You do not have permission to perform this action.';
      }
      if (detailLower.includes('timeout')) {
        return 'The operation timed out. Please try again.';
      }
      if (detailLower.includes('connection')) {
        return 'Cannot connect to the service. Please check if it is running.';
      }
    }

    // Use status code message if available
    if (statusMessages[status]) {
      return statusMessages[status];
    }

    return `Server error (${status}). Please try again or contact support.`;
  }

  // Handle network errors
  if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
    return 'Cannot connect to backend. Please ensure the backend server is running on port 54112.';
  }

  if (error.code === 'ECONNREFUSED') {
    return 'Connection refused. The service is not responding.';
  }

  if (error.code === 'ETIMEDOUT') {
    return 'Connection timed out. Please check your network connection.';
  }

  // Handle abort/cancel
  if (error.code === 'ERR_CANCELED') {
    return 'Request was cancelled.';
  }

  // Default fallback
  return error.message || 'An unexpected error occurred. Please try again.';
};

/**
 * Get error severity level for UI styling
 * @param {Error} error - The error object
 * @returns {string} Severity level: 'error', 'warning', or 'info'
 */
export const getErrorSeverity = (error) => {
  if (error.response) {
    const status = error.response.status;

    if (status >= 500) return 'error';
    if (status === 404) return 'warning';
    if (status === 401 || status === 403) return 'warning';
    if (status === 429) return 'info';

    return 'error';
  }

  if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
    return 'error';
  }

  if (error.code === 'ERR_CANCELED') {
    return 'info';
  }

  return 'error';
};

/**
 * Format error for display with title and description
 * @param {Error} error - The error object
 * @returns {Object} Object with title and description
 */
export const formatError = (error) => {
  const message = translateErrorMessage(error);
  const severity = getErrorSeverity(error);

  // Extract title from message (first sentence)
  const sentences = message.split('. ');
  const title = sentences[0] + (sentences.length > 1 ? '.' : '');
  const description = sentences.length > 1 ? sentences.slice(1).join('. ') : '';

  return {
    title,
    description,
    severity,
    fullMessage: message,
  };
};

export default translateErrorMessage;
