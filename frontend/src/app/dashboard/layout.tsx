'use client';

import React from 'react';
import Sidebar from '@/components/Sidebar';
import TopBar from '@/components/TopBar';
import AuthGuard from '@/components/AuthGuard';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#0A0E1A]">
        <Sidebar />
        <TopBar />
        <main>
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}