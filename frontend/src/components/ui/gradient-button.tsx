import { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GradientButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'as'> {
  children: ReactNode;
  isLoading?: boolean;
  fullWidth?: boolean;
  variant?: 'primary' | 'secondary';
  as?: 'button' | 'div';
}

export function GradientButton({
  children,
  isLoading,
  fullWidth,
  variant = 'primary',
  as: Component = 'button',
  className,
  disabled,
  ...props
}: GradientButtonProps) {
  const baseProps = {
    className: cn(
      'relative px-6 py-3 rounded-xl font-semibold text-sm',
      'transition-all duration-200',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      fullWidth && 'w-full',
      variant === 'primary' && [
        'bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6]',
        'text-white',
        'shadow-[0_4px_20px_rgba(46,155,255,0.4)]',
        'hover:scale-[1.02] hover:shadow-[0_8px_32px_rgba(46,155,255,0.6)]',
        'active:scale-[0.98]',
      ],
      variant === 'secondary' && [
        'bg-transparent border-2 border-[#2E9BFF]/50',
        'text-[#2E9BFF]',
        'hover:bg-[#2E9BFF]/10',
      ],
      className
    ),
    children: isLoading ? (
      <div className="flex items-center justify-center gap-2">
        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        <span>Loading...</span>
      </div>
    ) : (
      children
    ),
  };

  if (Component === 'div') {
    return <div {...baseProps} />;
  }

  return (
    <button
      {...baseProps}
      disabled={disabled || isLoading}
      {...props}
    />
  );
}

