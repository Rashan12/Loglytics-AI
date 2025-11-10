// API Configuration
// You can set NEXT_PUBLIC_API_URL in your environment or .env.local file
// Default: http://localhost:8000
export const API_BASE_URL = 'http://localhost:8000';
export const API_V1 = `${API_BASE_URL}/api/v1`;

export const API_ENDPOINTS = {
    // Auth
    login: `${API_V1}/auth/login`,
    register: `${API_V1}/auth/register`,
    me: `${API_V1}/auth/me`,
    
    // Chat - Use correct endpoints
    chat: `${API_V1}/chat`,
    conversations: `${API_V1}/chat/conversations`,
    conversationHistory: (id: string) => `${API_V1}/chat/history/${id}`,
    deleteConversation: (id: string) => `${API_V1}/chat/conversations/${id}`,
    
    // Projects
    projects: `${API_V1}/projects`,
    project: (id: string) => `${API_V1}/projects/${id}`,
    projectChat: (id: string) => `${API_V1}/projects/${id}/chat`,
    projectChatHistory: (id: string) => `${API_V1}/projects/${id}/chat/history`,
    
    // RAG Search endpoints
    ragSearch: `${API_V1}/rag/search`,
    ragStats: `${API_V1}/rag/stats`,
    ragHealth: `${API_V1}/rag/health`,
    
    // Log Files
    logFiles: `${API_V1}/logs/files`,
    uploadLog: `${API_V1}/logs/upload`,
    downloadLog: (id: string) => `${API_V1}/logs/files/${id}/download`,
    deleteLog: (id: string) => `${API_V1}/logs/files/${id}`,
    
    // Analytics
    analytics: `${API_V1}/analytics`,
    analyticsDashboard: `${API_V1}/analytics/dashboard`,
};

// Log API configuration for debugging
console.log('🔧 API Configuration:', {
    baseUrl: API_BASE_URL,
    v1: API_V1,
    endpoints: API_ENDPOINTS
});
