export const designTokens = {
  // Color Palette - Dark Mode Primary
  colors: {
    // Background layers (depth system)
    background: {
      primary: '#0A0E14',      // Deepest background
      secondary: '#0F1419',     // Card background
      tertiary: '#1A1F29',      // Elevated elements
      quaternary: '#24293A',    // Hover states
    },
    
    // Surface colors
    surface: {
      base: '#161B22',          // Base surface
      elevated: '#1C2128',      // Elevated cards
      overlay: '#252C36',       // Modals, dropdowns
    },
    
    // Text colors (hierarchy)
    text: {
      primary: '#E6EDF3',       // Primary text
      secondary: '#8B949E',     // Secondary text
      tertiary: '#6E7681',      // Tertiary text
      disabled: '#484F58',      // Disabled text
      inverse: '#0D1117',       // Text on light background
    },
    
    // Brand colors
    brand: {
      primary: '#3B82F6',       // Primary blue
      primaryHover: '#2563EB',  // Hover state
      secondary: '#8B5CF6',     // Secondary purple
      accent: '#10B981',        // Success green
    },
    
    // Semantic colors
    semantic: {
      success: '#10B981',       // Green
      warning: '#F59E0B',       // Amber
      error: '#EF4444',         // Red
      info: '#3B82F6',          // Blue
    },
    
    // Status colors
    status: {
      online: '#10B981',
      offline: '#6B7280',
      pending: '#F59E0B',
      error: '#EF4444',
    },
    
    // Chart colors (professional palette)
    charts: {
      primary: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'],
      gradient: {
        blue: ['#3B82F6', '#1D4ED8'],
        purple: ['#8B5CF6', '#6D28D9'],
        green: ['#10B981', '#059669'],
      }
    },
    
    // Border colors
    border: {
      subtle: '#30363D',        // Subtle borders
      default: '#444D56',       // Default borders
      strong: '#6E7681',        // Strong borders
      focus: '#3B82F6',         // Focus state
    },
  },
  
  // Typography System
  typography: {
    fontFamily: {
      sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
    },
    
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
    },
    
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  
  // Spacing System (8px base)
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.25rem',    // 4px
    base: '0.5rem',   // 8px
    md: '0.75rem',    // 12px
    lg: '1rem',       // 16px
    xl: '1.5rem',     // 24px
    full: '9999px',
  },
  
  // Shadows (neumorphic + material)
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
    base: '0 2px 4px -1px rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.4)',
    
    // Neumorphic shadows
    neumorphic: {
      raised: '8px 8px 16px rgba(0, 0, 0, 0.5), -8px -8px 16px rgba(255, 255, 255, 0.05)',
      pressed: 'inset 8px 8px 16px rgba(0, 0, 0, 0.5), inset -8px -8px 16px rgba(255, 255, 255, 0.05)',
    },
    
    // Glow effects
    glow: {
      blue: '0 0 20px rgba(59, 130, 246, 0.3)',
      purple: '0 0 20px rgba(139, 92, 246, 0.3)',
      green: '0 0 20px rgba(16, 185, 129, 0.3)',
    },
  },
  
  // Animation & Transitions
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    smooth: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
  
  // Z-index layers
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    modal: 1200,
    popover: 1300,
    tooltip: 1400,
    notification: 1500,
  },
};

export default designTokens;
