import { create } from "zustand"
import { persist } from "zustand/middleware"

interface UIState {
  sidebarCollapsed: boolean
  sidebarMobileOpen: boolean
  theme: "light" | "dark" | "system"
  toastQueue: Array<{
    id: string
    title: string
    description?: string
    type: "success" | "error" | "warning" | "info"
    duration?: number
  }>
  modals: {
    createProject: boolean
    createChat: boolean
    settings: boolean
    help: boolean
  }
  loading: {
    global: boolean
    projects: boolean
    analytics: boolean
    liveLogs: boolean
  }
}

interface UIActions {
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebarMobile: () => void
  setSidebarMobileOpen: (open: boolean) => void
  setTheme: (theme: "light" | "dark" | "system") => void
  addToast: (toast: Omit<UIState["toastQueue"][0], "id">) => void
  removeToast: (id: string) => void
  clearToasts: () => void
  setModal: (modal: keyof UIState["modals"], open: boolean) => void
  setLoading: (key: keyof UIState["loading"], loading: boolean) => void
  reset: () => void
}

const initialState: UIState = {
  sidebarCollapsed: false,
  sidebarMobileOpen: false,
  theme: "dark",
  toastQueue: [],
  modals: {
    createProject: false,
    createChat: false,
    settings: false,
    help: false,
  },
  loading: {
    global: false,
    projects: false,
    analytics: false,
    liveLogs: false,
  },
}

export const useUIStore = create<UIState & UIActions>()(
  persist(
    (set, get) => ({
      ...initialState,

      toggleSidebar: () => {
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed,
        }))
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed })
      },

      toggleSidebarMobile: () => {
        set((state) => ({
          sidebarMobileOpen: !state.sidebarMobileOpen,
        }))
      },

      setSidebarMobileOpen: (open) => {
        set({ sidebarMobileOpen: open })
      },

      setTheme: (theme) => {
        set({ theme })
      },

      addToast: (toast) => {
        const id = Math.random().toString(36).substr(2, 9)
        set((state) => ({
          toastQueue: [...state.toastQueue, { ...toast, id }],
        }))

        // Auto remove toast after duration
        const duration = toast.duration || 5000
        setTimeout(() => {
          get().removeToast(id)
        }, duration)
      },

      removeToast: (id) => {
        set((state) => ({
          toastQueue: state.toastQueue.filter((toast) => toast.id !== id),
        }))
      },

      clearToasts: () => {
        set({ toastQueue: [] })
      },

      setModal: (modal, open) => {
        set((state) => ({
          modals: {
            ...state.modals,
            [modal]: open,
          },
        }))
      },

      setLoading: (key, loading) => {
        set((state) => ({
          loading: {
            ...state.loading,
            [key]: loading,
          },
        }))
      },

      reset: () => {
        set(initialState)
      },
    }),
    {
      name: "ui-store",
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
)
