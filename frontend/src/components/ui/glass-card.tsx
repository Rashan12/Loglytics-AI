import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function GlassCard({ children, className, hover = false }: GlassCardProps) {
  return (
    <div
      className={cn(
        'relative rounded-2xl p-8',
        'bg-[rgba(26,31,58,0.6)] backdrop-blur-xl',
        'border border-white/10',
        'shadow-[0_8px_32px_rgba(0,0,0,0.4)]',
        hover && 'transition-all duration-300 hover:border-[#2E9BFF]/50 hover:-translate-y-1',
        className
      )}
    >
      {children}
    </div>
  );
}

