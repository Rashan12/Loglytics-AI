'use client';

import { useEffect } from 'react';

/**
 * Global fetch interceptor to:
 * 1. Suppress 404 errors for expected endpoints
 * 2. Handle 401 authentication errors by redirecting to login
 */
export function FetchInterceptor() {
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;

    // Store original fetch
    const originalFetch = window.fetch;

    // URLs that should silently handle 404s
    const silent404Urls = [
      '/api/v1/live-logs/alerts',
      '/api/v1/logs/files',
    ];

    // URLs that should NOT trigger auto-logout on 401 (public endpoints)
    const publicUrls = [
      '/api/v1/auth/login',
      '/api/v1/auth/register',
      '/api/v1/auth/refresh',
    ];

    // Override fetch globally
    window.fetch = async function(...args: Parameters<typeof fetch>): Promise<Response> {
      const url = typeof args[0] === 'string' ? args[0] : (args[0] as Request).url;
      
      // Check if this URL should silently handle 404s
      const shouldSilence = silent404Urls.some(silentUrl => url.includes(silentUrl));
      
      // Check if this is a public endpoint (don't logout on 401)
      const isPublic = publicUrls.some(publicUrl => url.includes(publicUrl));
      
      try {
        const response = await originalFetch.apply(this, args);
        
        // Handle 401 Unauthorized - token invalid/expired
        if (response.status === 401 && !isPublic) {
          console.warn('🔒 Authentication failed. Token invalid or expired. Redirecting to login...');
          
          // Clear all auth data
          localStorage.removeItem('access_token');
          localStorage.removeItem('auth-store');
          
          // Only redirect if we're not already on login/register page
          if (!window.location.pathname.includes('/login') && 
              !window.location.pathname.includes('/register')) {
            // Small delay to prevent multiple redirects
            setTimeout(() => {
              window.location.href = '/login';
            }, 100);
          }
          
          // Return the 401 response so components can handle it
          return response;
        }
        
        // If it's a 404 for a silent URL, return a successful empty response
        if (response.status === 404 && shouldSilence) {
          // Return empty array response with 200 status to prevent console error
          return new Response(JSON.stringify([]), {
            status: 200,
            statusText: 'OK',
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }
        
        return response;
      } catch (error) {
        // For network errors on silent URLs, return empty response
        if (shouldSilence) {
          return new Response(JSON.stringify([]), {
            status: 200,
            statusText: 'OK',
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }
        throw error;
      }
    } as typeof fetch;

    // Cleanup: restore original fetch on unmount
    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  return null; // This component doesn't render anything
}

