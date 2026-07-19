const API_BASE = import.meta.env.VITE_API_URL || '';

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  getProfile: (userId = 'default') =>
    apiCall(`/api/profile/${userId}`),

  updateProfile: (profile) =>
    apiCall('/api/profile', { method: 'POST', body: JSON.stringify(profile) }),

  sendMessage: (message, userId = 'default') =>
    apiCall('/api/chat', { method: 'POST', body: JSON.stringify({ message, user_id: userId }) }),

  getChatHistory: (userId = 'default') =>
    apiCall(`/api/chat/history/${userId}`),

  getDashboard: (userId = 'default') =>
    apiCall(`/api/dashboard/${userId}`),

  getRenphoStatus: (userId = 'default') =>
    apiCall(`/api/renpho/status?user_id=${userId}`),

  getRenphoLatest: (userId = 'default') =>
    apiCall(`/api/renpho/latest?user_id=${userId}`),

  generateNutritionPlan: (userId = 'default') =>
    apiCall(`/api/nutrition/plan?user_id=${userId}`, { method: 'POST' }),

  generateWorkoutPlan: (userId = 'default') =>
    apiCall(`/api/workout/plan?user_id=${userId}`, { method: 'POST' }),

  healthCheck: () =>
    apiCall('/api/health'),

  getGoogleFitUrl: (userId = 'default') =>
    apiCall(`/api/google-fit/url?user_id=${userId}`),

  googleFitCallback: (code, userId = 'default') =>
    apiCall('/api/google-fit/callback', { method: 'POST', body: JSON.stringify({ code, user_id: userId }) }),

  getGoogleFitStatus: (userId = 'default') =>
    apiCall(`/api/google-fit/status?user_id=${userId}`),

  getGoogleFitHistory: (userId = 'default', days = 30) =>
    apiCall(`/api/google-fit/history?user_id=${userId}&days=${days}`),

  getYazioStatus: (userId = 'default') =>
    apiCall(`/api/yazio/status?user_id=${userId}`),

  getYazioDaily: (userId = 'default', date) =>
    apiCall(`/api/yazio/daily?user_id=${userId}${date ? `&date=${date}` : ''}`),

  getYazioDiary: (userId = 'default', date) =>
    apiCall(`/api/yazio/diary?user_id=${userId}${date ? `&date=${date}` : ''}`),

  listUsers: () =>
    apiCall('/api/users'),

  getUser: (userId) =>
    apiCall(`/api/users/${userId}`),

  createUser: (id, name, renphoEmail = '', renphoPassword = '', yazioEmail = '', yazioPassword = '') =>
    apiCall('/api/users', {
      method: 'POST',
      body: JSON.stringify({ id, name, renpho_email: renphoEmail, renpho_password: renphoPassword, yazio_email: yazioEmail, yazio_password: yazioPassword })
    }),

  updateUser: (userId, data) =>
    apiCall(`/api/users/${userId}`, { method: 'PUT', body: JSON.stringify(data) }),

  deleteUser: (userId) =>
    apiCall(`/api/users/${userId}`, { method: 'DELETE' }),

  refreshAll: () =>
    apiCall('/api/refresh', { method: 'POST' }),
};
