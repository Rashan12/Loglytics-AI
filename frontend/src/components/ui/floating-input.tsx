'use client';

import { InputHTMLAttributes, useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { Eye, EyeOff } from 'lucide-react';

interface FloatingInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function FloatingInput({ 
  label, 
  error, 
  type = 'text',
  className,
  ...props 
}: FloatingInputProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const hasValue = props.value && String(props.value).length > 0;

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';
  const inputType = type === 'password' && showPassword ? 'text' : type;

  return (
    <div className="relative">
      <input
        type={inputType}
        className={cn(
          'peer w-full px-4 pt-6 pb-2 rounded-xl',
          'border transition-all duration-200',
          'placeholder-transparent text-base',
          'focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20',
          isDark
            ? 'bg-[#0D1117]/60 backdrop-blur-sm border-white/10 text-[#F9FAFB] focus:border-[#2E9BFF]'
            : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500',
          error && 'border-[#EF4444] focus:border-[#EF4444] focus:ring-[#EF4444]/20',
          className
        )}
        placeholder={label}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        {...props}
      />
      
      <label
        className={cn(
          'absolute left-4 transition-all duration-200 pointer-events-none',
          isDark ? 'text-[#9CA3AF]' : 'text-gray-500',
          (isFocused || hasValue) ? 'top-2 text-xs' : 'top-4 text-base'
        )}
      >
        {label}
      </label>

      {type === 'password' && (
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className={cn(
            'absolute right-4 top-1/2 -translate-y-1/2 transition-colors',
            isDark ? 'text-[#9CA3AF] hover:text-[#2E9BFF]' : 'text-gray-400 hover:text-blue-600'
          )}
        >
          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
        </button>
      )}

      {error && (
        <p className="mt-1.5 text-xs text-[#EF4444]">{error}</p>
      )}
    </div>
  );
}

