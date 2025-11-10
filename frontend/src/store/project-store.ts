import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  is_active?: boolean;
  log_files_count?: number;
  user_id?: string;
}

// Helper function to get token
const getToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  
  // Try direct localStorage key first (most common)
  const directToken = localStorage.getItem('access_token');
  if (directToken) {
    return directToken;
  }
  
  // Try auth store persisted state (zustand persist format)
  try {
    const authStoreData = localStorage.getItem('auth-store');
    if (authStoreData) {
      const parsed = JSON.parse(authStoreData);
      // Zustand persist stores data as { state: { token: ... } }
      if (parsed?.state?.token) {
        return parsed.state.token;
      }
      // Sometimes it's stored directly
      if (parsed?.token) {
        return parsed.token;
      }
    }
  } catch (e) {
    console.warn('Failed to parse auth-store:', e);
  }
  
  console.warn('⚠️ No token found in localStorage');
  return null;
};

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<Project | null>;
  createProject: (name: string, description?: string) => Promise<Project | null>;
  updateProject: (id: string, updates: Partial<Project>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,

      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const token = getToken();
          if (!token) {
            console.warn('⚠️ No token found for fetching projects');
            set({ projects: [], isLoading: false });
            // Redirect to login if no token
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
            return;
          }

          const response = await fetch('http://localhost:8000/api/v1/projects', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          // Handle 401 Unauthorized - token invalid/expired
          if (response.status === 401) {
            console.warn('🔒 Authentication failed. Token invalid or expired.');
            // Clear auth data
            localStorage.removeItem('access_token');
            localStorage.removeItem('auth-store');
            set({ projects: [], isLoading: false, error: 'Authentication failed. Please log in again.' });
            // Redirect to login
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
            return;
          }

          if (!response.ok) {
            throw new Error(`Failed to fetch projects: ${response.status} ${response.statusText}`);
          }

          const data = await response.json();
          // Handle both { projects: [...] } and direct array response
          const projects = Array.isArray(data) ? data : (data.projects || []);
          
          console.log('📦 Fetched projects:', projects.length, 'projects');
          console.log('📦 Project data:', projects);
          
          set({ projects, isLoading: false });
        } catch (error) {
          console.error('❌ Error fetching projects:', error);
          set({ 
            error: (error as Error).message, 
            isLoading: false,
            projects: []
          });
        }
      },

      fetchProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const token = getToken();
          if (!token) {
            throw new Error('No authentication token found. Please log in again.');
          }
          const response = await fetch(`http://localhost:8000/api/v1/projects/${id}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          // Handle 401 Unauthorized - token invalid/expired
          if (response.status === 401) {
            console.warn('🔒 Authentication failed. Token invalid or expired.');
            localStorage.removeItem('access_token');
            localStorage.removeItem('auth-store');
            set({ currentProject: null, isLoading: false, error: 'Authentication failed. Please log in again.' });
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
            throw new Error('Authentication failed. Please log in again.');
          }

          if (!response.ok) {
            throw new Error(`Failed to fetch project: ${response.status} ${response.statusText}`);
          }

          const project = await response.json();
          set({ currentProject: project, isLoading: false });
          return project;
        } catch (error) {
          set({ 
            error: (error as Error).message, 
            isLoading: false 
          });
          return null;
        }
      },

      createProject: async (name: string, description?: string) => {
        set({ isLoading: true, error: null });
        try {
          const token = getToken();
          if (!token) {
            throw new Error('No authentication token found. Please log in again.');
          }
          
          console.log('🔑 Using token for project creation:', token ? 'Token found' : 'No token');

          const response = await fetch('http://localhost:8000/api/v1/projects', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description }),
          });

          if (!response.ok) {
            if (response.status === 401) {
              throw new Error('Authentication expired. Please log in again.');
            }
            const errorData = await response.json().catch(() => ({ detail: 'Failed to create project' }));
            throw new Error(errorData.detail || `Failed to create project: ${response.status}`);
          }

          const project = await response.json();
          set((state) => ({
            projects: [...state.projects, project],
            isLoading: false,
          }));
          return project;
        } catch (error) {
          const errorMessage = (error as Error).message;
          console.error('Error creating project:', errorMessage);
          set({ 
            error: errorMessage, 
            isLoading: false 
          });
          return null;
        }
      },

      updateProject: async (id: string, updates: Partial<Project>) => {
        set({ isLoading: true, error: null });
        try {
          const token = getToken();
          if (!token) {
            throw new Error('No authentication token found. Please log in again.');
          }
          const response = await fetch(`http://localhost:8000/api/v1/projects/${id}`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates),
          });

          if (!response.ok) {
            throw new Error('Failed to update project');
          }

          const updatedProject = await response.json();
          set((state) => ({
            projects: state.projects.map(p => p.id === id ? updatedProject : p),
            currentProject: state.currentProject?.id === id ? updatedProject : state.currentProject,
            isLoading: false,
          }));
        } catch (error) {
          set({ 
            error: (error as Error).message, 
            isLoading: false 
          });
        }
      },

      deleteProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const token = getToken();
          if (!token) {
            throw new Error('No authentication token found. Please log in again.');
          }
          const response = await fetch(`http://localhost:8000/api/v1/projects/${id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Failed to delete project');
          }

          set((state) => ({
            projects: state.projects.filter(p => p.id !== id),
            currentProject: state.currentProject?.id === id ? null : state.currentProject,
            isLoading: false,
          }));
        } catch (error) {
          set({ 
            error: (error as Error).message, 
            isLoading: false 
          });
        }
      },

      setCurrentProject: (project) => {
        set({ currentProject: project });
      },
    }),
    {
      name: 'project-store',
      partialize: (state) => ({
        currentProject: state.currentProject,
      }),
    }
  )
);

