'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface EnhancedCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'neumorphic' | 'gradient' | 'elevated';
  hover?: boolean;
  glow?: boolean;
  children: React.ReactNode;
}

const EnhancedCard = React.forwardRef<HTMLDivElement, EnhancedCardProps>(
  ({ className, variant = 'default', hover = true, glow = false, children, ...props }, ref) => {
    const baseClasses = "rounded-xl border transition-all duration-300";
    
    const variantClasses = {
      default: "bg-[#1C2128] border-[#30363D] text-white",
      glass: "glass border-white/20 backdrop-blur-xl",
      neumorphic: "neumorphic border-transparent",
      gradient: "bg-gradient-to-br from-blue-600/20 to-purple-600/20 border-blue-500/30",
      elevated: "bg-[#1C2128] border-[#30363D] shadow-lg shadow-black/20",
    };

    const hoverClasses = hover ? "card-hover" : "";
    const glowClasses = glow ? "shadow-glow-blue" : "";

    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className={cn(
          baseClasses,
          variantClasses[variant],
          hoverClasses,
          glowClasses,
          className
        )}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

EnhancedCard.displayName = 'EnhancedCard';

const EnhancedCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-2 p-6 pb-4", className)}
    {...props}
  />
));

EnhancedCardHeader.displayName = 'EnhancedCardHeader';

const EnhancedCardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-xl font-semibold leading-none tracking-tight text-white",
      className
    )}
    {...props}
  />
));

EnhancedCardTitle.displayName = 'EnhancedCardTitle';

const EnhancedCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-gray-400", className)}
    {...props}
  />
));

EnhancedCardDescription.displayName = 'EnhancedCardDescription';

const EnhancedCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));

EnhancedCardContent.displayName = 'EnhancedCardContent';

const EnhancedCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));

EnhancedCardFooter.displayName = 'EnhancedCardFooter';

export {
  EnhancedCard,
  EnhancedCardHeader,
  EnhancedCardTitle,
  EnhancedCardDescription,
  EnhancedCardContent,
  EnhancedCardFooter,
};
