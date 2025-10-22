'use client';

import { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string;
    trend: 'up' | 'down';
  };
  icon: LucideIcon;
  iconColor?: 'blue' | 'green' | 'purple' | 'orange';
}

const iconColorClasses = {
  blue: 'bg-blue-500/10 text-blue-500 border-blue-500/30',
  green: 'bg-green-500/10 text-green-500 border-green-500/30',
  purple: 'bg-purple-500/10 text-purple-500 border-purple-500/30',
  orange: 'bg-orange-500/10 text-orange-500 border-orange-500/30',
};

export default function StatCard({ 
  title, 
  value, 
  change, 
  icon: Icon,
  iconColor = 'blue' 
}: StatCardProps) {
  return (
    <div className="group relative bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10 hover:-translate-y-1">
      {/* Background gradient on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-purple-600/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm text-gray-400 font-medium">{title}</p>
            <h3 className="text-3xl font-bold text-white mt-2">{value.toLocaleString()}</h3>
          </div>
          
          <div className={`p-3 rounded-lg border ${iconColorClasses[iconColor]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>

        {/* Change indicator */}
        {change && (
          <div className="flex items-center gap-2">
            {change.trend === 'up' ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
            <span className={`text-sm font-semibold ${
              change.trend === 'up' ? 'text-green-500' : 'text-red-500'
            }`}>
              {change.value}
            </span>
            <span className="text-sm text-gray-500">from last period</span>
          </div>
        )}
      </div>
    </div>
  );
}
