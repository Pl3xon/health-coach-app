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
  // Profile
  getProfile: (userId = 'default') => 
    apiCall(`/api/profile/${userId}`),
  
  updateProfile: (profile) => 
    apiCall('/api/profile', { method: 'POST', body: JSON.stringify(profile) }),

  // Chat
  sendMessage: (message, userId = 'default') => 
    apiCall('/api/chat', { method: 'POST', body: JSON.stringify({ message, user_id: userId }) }),
  
  getChatHistory: (userId = 'default') => 
    apiCall(`/api/chat/history/${userId}`),

  // Dashboard
  getDashboard: (userId = 'default') => 
    apiCall(`/api/dashboard/${userId}`),

  // Renpho
  getRenphoStatus: () => 
    apiCall('/api/renpho/status'),
  
  getRenphoLatest: () => 
    apiCall('/api/renpho/latest'),

  // Plans
  generateNutritionPlan: (userId = 'default') => 
    apiCall(`/api/nutrition/plan?user_id=${userId}`, { method: 'POST' }),
  
  generateWorkoutPlan: (userId = 'default') => 
    apiCall(`/api/workout/plan?user_id=${userId}`, { method: 'POST' }),

  // Health
  healthCheck: () => 
    apiCall('/api/health'),

  // Google Fit
  getGoogleFitUrl: () => 
    apiCall('/api/google-fit/url'),
  
  googleFitCallback: (code) => 
    apiCall('/api/google-fit/callback', { method: 'POST', body: JSON.stringify({ code }) }),
  
  getGoogleFitStatus: () => 
    apiCall('/api/google-fit/status'),

  getGoogleFitHistory: (days = 30) => 
    apiCall(`/api/google-fit/history?days=${days}`),

  // Yazio
  getYazioStatus: () => 
    apiCall('/api/yazio/status'),
  
  getYazioDaily: (date) => 
    apiCall(`/api/yazio/daily${date ? `?date=${date}` : ''}`),
  
  getYazioDiary: (date) => 
    apiCall(`/api/yazio/diary${date ? `?date=${date}` : ''}`),
};
