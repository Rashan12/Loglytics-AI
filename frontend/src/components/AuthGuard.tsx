'use client';

import { useEffect, useState } from 'react';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      // Check both localStorage and auth store
      const tokenFromStorage = localStorage.getItem('access_token');
      const authStore = JSON.parse(localStorage.getItem('auth-store') || '{}');
      const tokenFromStore = authStore?.state?.token;
      
      const token = tokenFromStorage || tokenFromStore;
      
      if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = '/login';
        return;
      }
      
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expiry = payload.exp * 1000;
        const now = Date.now();
        
        // Check if token expired
        if (now >= expiry) {
          console.log('❌ Token expired, redirecting to login');
          localStorage.clear();
          window.location.href = '/login';
          return;
        }
        
        // Check if token expires in less than 1 day - warn user
        const daysUntilExpiry = (expiry - now) / (1000 * 60 * 60 * 24);
        if (daysUntilExpiry < 1) {
          console.warn(`⚠️ Token expires in ${daysUntilExpiry.toFixed(1)} days`);
        }
        
        console.log('✅ Token valid');
        setMounted(true);
        
      } catch (error) {
        console.error('❌ Token validation error:', error);
        localStorage.clear();
        window.location.href = '/login';
      }
    };
    
    checkAuth();
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#0A0E14] flex items-center justify-center">
        <div className="text-white">Verifying authentication...</div>
      </div>
    );
  }

  return <>{children}</>;
}
