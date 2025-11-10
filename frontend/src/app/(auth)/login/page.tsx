'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Activity, ArrowRight, Mail, Lock, Sparkles, Zap, Shield } from 'lucide-react';
import { ParticleBackground } from '@/components/auth/particle-background';
import { GlassCard } from '@/components/ui/glass-card';
import { GradientButton } from '@/components/ui/gradient-button';
import { FloatingInput } from '@/components/ui/floating-input';
import { useAuthStore } from '@/store/auth-store';
import { apiClient, handleApiError } from '@/lib/api';
import { toast } from 'sonner';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuthStore();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    const newErrors: Record<string, string> = {};
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await apiClient.post<{
        access_token: string;
        token_type: string;
        user: any;
      }>('/auth/login', formData);

      const { access_token, user } = response.data;

      // Store tokens and user data (use access_token as refresh_token for now)
      login(user, access_token, access_token);
      
      // Also store in localStorage for compatibility
      localStorage.setItem('access_token', access_token);
      
      toast.success("Welcome back!", {
        description: "You have been successfully logged in.",
      });

      router.push('/dashboard');
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      setErrors({ general: errorMessage || 'Login failed. Please check your credentials.' });
      toast.error("Login failed", {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E1A] flex">
      {/* Left Side - Hero Section */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Particle Background */}
        <ParticleBackground />
        
        {/* Grid Pattern Overlay */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(46,155,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(46,155,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '32px 32px',
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-16 w-full">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-12"
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] rounded-2xl blur-xl opacity-50 animate-pulse" />
                <div className="relative p-3 bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] rounded-2xl shadow-lg">
                  <Activity className="w-8 h-8 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-[#F9FAFB]">Loglytics AI</h1>
                <p className="text-sm text-[#9CA3AF]">Intelligent Log Analysis</p>
              </div>
            </div>
          </motion.div>

          {/* Hero Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h2 className="text-5xl font-bold text-[#F9FAFB] mb-6 leading-tight">
              AI-Powered
              <br />
              <span className="bg-gradient-to-r from-[#2E9BFF] via-[#8B5CF6] to-[#00D9FF] bg-clip-text text-transparent">
                Log Intelligence
              </span>
            </h2>
            
            <p className="text-lg text-[#D1D5DB] mb-12 max-w-md">
              Real-time monitoring meets artificial intelligence. Transform your logs into actionable insights.
            </p>

            {/* Features */}
            <div className="space-y-4">
              <FeatureItem icon={Sparkles} text="AI-powered error detection and analysis" />
              <FeatureItem icon={Zap} text="Real-time log streaming and alerts" />
              <FeatureItem icon={Shield} text="Enterprise-grade security and compliance" />
            </div>
          </motion.div>

          {/* Floating Mock Screenshots */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="absolute bottom-8 right-8 w-96"
          >
            <GlassCard className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                <div className="w-3 h-3 rounded-full bg-[#10B981]" />
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="text-[#10B981]">[2024-01-15 10:30:45] INFO Request processed</div>
                <div className="text-[#EF4444]">[2024-01-15 10:30:46] ERROR Connection timeout</div>
                <div className="text-[#F59E0B]">[2024-01-15 10:30:47] WARN High memory usage</div>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        {/* Background for mobile */}
        <div className="absolute inset-0 lg:hidden">
          <ParticleBackground />
          <div className="absolute inset-0 bg-[#0A0E1A]/80 backdrop-blur-sm" />
        </div>

        {/* Form Container */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="relative z-10 w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] rounded-2xl blur-xl opacity-50" />
                <div className="relative p-3 bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] rounded-2xl">
                  <Activity className="w-6 h-6 text-white" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-[#F9FAFB]">Loglytics AI</h1>
            </div>
          </div>

          <GlassCard>
            {/* Header */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-[#F9FAFB] mb-2">Welcome back</h2>
              <p className="text-[#9CA3AF]">Sign in to your account to continue</p>
            </div>

            {/* Error Message */}
            {errors.general && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/50"
              >
                <p className="text-sm text-[#EF4444]">{errors.general}</p>
              </motion.div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <FloatingInput
                label="Email address"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                error={errors.email}
                autoComplete="email"
              />

              <FloatingInput
                label="Password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                error={errors.password}
                autoComplete="current-password"
              />

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-[#D1D5DB] cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-white/10 bg-[rgba(13,17,23,0.6)] text-[#2E9BFF] focus:ring-2 focus:ring-[#2E9BFF]/20"
                  />
                  <span>Remember me</span>
                </label>
                <Link href="/forgot-password" className="text-[#2E9BFF] hover:text-[#00D9FF] transition-colors">
                  Forgot password?
                </Link>
              </div>

              <GradientButton
                type="submit"
                fullWidth
                isLoading={isLoading}
                className="py-4 text-base"
              >
                {!isLoading && (
                  <>
                    Sign in
                    <ArrowRight className="w-5 h-5 ml-2 inline" />
                  </>
                )}
              </GradientButton>
            </form>

            {/* Divider */}
            <div className="my-8 flex items-center gap-4">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-sm text-[#6B7280]">Or continue with</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

            {/* Social Login */}
            <div className="grid grid-cols-2 gap-4">
              <button 
                type="button"
                className="px-4 py-3 rounded-xl bg-[rgba(13,17,23,0.6)] border border-white/10 text-[#D1D5DB] hover:bg-white/5 hover:border-[#2E9BFF]/50 transition-all duration-200 flex items-center justify-center gap-2"
                onClick={() => toast.info("Coming soon", { description: "Google login will be available soon." })}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Google
              </button>
              
              <button 
                type="button"
                className="px-4 py-3 rounded-xl bg-[rgba(13,17,23,0.6)] border border-white/10 text-[#D1D5DB] hover:bg-white/5 hover:border-[#2E9BFF]/50 transition-all duration-200 flex items-center justify-center gap-2"
                onClick={() => toast.info("Coming soon", { description: "GitHub login will be available soon." })}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </button>
            </div>

            {/* Sign Up Link */}
            <div className="mt-8 text-center">
              <p className="text-[#9CA3AF]">
                Don't have an account?{' '}
                <Link 
                  href="/register" 
                  className="text-[#2E9BFF] hover:text-[#00D9FF] font-semibold transition-colors"
                >
                  Sign up
                </Link>
              </p>
            </div>
          </GlassCard>

          {/* Footer */}
          <p className="mt-8 text-center text-sm text-[#6B7280]">
            By signing in, you agree to our{' '}
            <a href="#" className="text-[#2E9BFF] hover:underline">Terms</a>
            {' '}and{' '}
            <a href="#" className="text-[#2E9BFF] hover:underline">Privacy Policy</a>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

function FeatureItem({ icon: Icon, text }: { icon: any; text: string }) {
  return (
    <div className="flex items-center gap-3 text-[#D1D5DB]">
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 border border-[#2E9BFF]/30 flex items-center justify-center">
        <Icon className="w-5 h-5 text-[#2E9BFF]" />
      </div>
      <span className="text-sm">{text}</span>
    </div>
  );
}
