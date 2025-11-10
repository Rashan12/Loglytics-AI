'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Activity, ArrowRight, User, Mail, Lock, Sparkles, Zap, Shield } from 'lucide-react';
import { ParticleBackground } from '@/components/auth/particle-background';
import { GlassCard } from '@/components/ui/glass-card';
import { GradientButton } from '@/components/ui/gradient-button';
import { FloatingInput } from '@/components/ui/floating-input';
import { useAuthStore } from '@/store/auth-store';
import { apiClient, handleApiError } from '@/lib/api';
import { toast } from 'sonner';

export default function RegisterPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuthStore();
  
  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    const newErrors: Record<string, string> = {};
    if (!formData.fullName) newErrors.fullName = 'Full name is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      // Send registration data (matching existing register form format)
      const registrationData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || undefined,
      };

      const response = await apiClient.post<{
        access_token: string;
        refresh_token: string;
        token_type: string;
        user: any;
      }>('/auth/register', registrationData);

      const { access_token, refresh_token, user } = response.data;

      // Store tokens and user data
      login(user, access_token, refresh_token);

      toast.success("Account created!", {
        description: "Welcome to Loglytics AI. Your account has been created successfully.",
      });

      router.push('/dashboard');
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      setErrors({ general: errorMessage || 'Registration failed. Please try again.' });
      toast.error("Registration failed", {
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
        <ParticleBackground />
        
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

        <div className="relative z-10 flex flex-col justify-center px-16 w-full">
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

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h2 className="text-5xl font-bold text-[#F9FAFB] mb-6 leading-tight">
              Start your
              <br />
              <span className="bg-gradient-to-r from-[#2E9BFF] via-[#8B5CF6] to-[#00D9FF] bg-clip-text text-transparent">
                AI Journey
              </span>
            </h2>
            
            <p className="text-lg text-[#D1D5DB] mb-12 max-w-md">
              Join thousands of teams using AI-powered log analysis to build better products.
            </p>

            <div className="space-y-4">
              <FeatureItem icon={Sparkles} text="Get started in under 2 minutes" />
              <FeatureItem icon={Zap} text="No credit card required" />
              <FeatureItem icon={Shield} text="14-day free trial included" />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <div className="absolute inset-0 lg:hidden">
          <ParticleBackground />
          <div className="absolute inset-0 bg-[#0A0E1A]/80 backdrop-blur-sm" />
        </div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="relative z-10 w-full max-w-md"
        >
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
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-[#F9FAFB] mb-2">Create account</h2>
              <p className="text-[#9CA3AF]">Start your free trial today</p>
            </div>

            {errors.general && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/50"
              >
                <p className="text-sm text-[#EF4444]">{errors.general}</p>
              </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <FloatingInput
                label="Full name"
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                error={errors.fullName}
                autoComplete="name"
              />

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
                autoComplete="new-password"
              />

              <FloatingInput
                label="Confirm password"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                error={errors.confirmPassword}
                autoComplete="new-password"
              />

              <GradientButton
                type="submit"
                fullWidth
                isLoading={isLoading}
                className="py-4 text-base"
              >
                {!isLoading && (
                  <>
                    Create account
                    <ArrowRight className="w-5 h-5 ml-2 inline" />
                  </>
                )}
              </GradientButton>
            </form>

            <div className="my-8 flex items-center gap-4">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-sm text-[#6B7280]">Or sign up with</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

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

            <div className="mt-8 text-center">
              <p className="text-[#9CA3AF]">
                Already have an account?{' '}
                <Link 
                  href="/login" 
                  className="text-[#2E9BFF] hover:text-[#00D9FF] font-semibold transition-colors"
                >
                  Sign in
                </Link>
              </p>
            </div>
          </GlassCard>

          <p className="mt-8 text-center text-sm text-[#6B7280]">
            By creating an account, you agree to our{' '}
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
