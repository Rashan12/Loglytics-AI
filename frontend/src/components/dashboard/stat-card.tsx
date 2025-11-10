'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  gradient: string;
  isDark?: boolean;
}

export function StatCard({ title, value, icon: Icon, trend, trendUp, gradient, isDark = true }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'relative p-6 rounded-2xl border transition-all overflow-hidden group',
        isDark 
          ? 'bg-[#1A1F3A]/60 backdrop-blur-xl border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50' 
          : 'bg-white border-gray-200 hover:border-blue-300 shadow-sm hover:shadow-lg'
      )}
    >
      {/* Grid Pattern Overlay */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(46,155,255,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(46,155,255,0.3) 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px',
        }}
      />

      {/* Gradient Blob */}
      <div className={`absolute top-0 right-0 w-32 h-32 ${gradient} rounded-full blur-3xl opacity-20 group-hover:opacity-30 transition-opacity`} />

      <div className="relative">
        {/* Icon and Trend */}
        <div className="flex items-start justify-between mb-4">
          <div className={cn(
            `p-3 rounded-xl ${gradient} bg-opacity-20 border`,
            isDark ? 'border-[#2E3A5C]' : 'border-gray-200'
          )}>
            <Icon className="w-6 h-6 text-[#2E9BFF]" />
          </div>
          {trend && (
            <span className={`text-sm font-semibold ${trendUp ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
              {trendUp ? '↑' : '↓'} {trend}
            </span>
          )}
        </div>

        {/* Value - REASONABLE SIZE */}
        <div className="mb-1">
          <div className={cn(
            'text-3xl font-bold',
            isDark 
              ? 'bg-gradient-to-r from-[#F9FAFB] to-[#D1D5DB] bg-clip-text text-transparent' 
              : 'text-gray-900'
          )}>
            {value}
          </div>
        </div>

        {/* Title */}
        <div className={cn(
          'text-sm font-medium',
          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
        )}>
          {title}
        </div>
      </div>
    </motion.div>
  );
}

