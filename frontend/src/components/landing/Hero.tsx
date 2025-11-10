'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Sparkles, Star } from 'lucide-react';
import { landingContent } from '@/lib/landing-content';
import { AIBrain } from '@/components/3d/AIBrain';

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0A0E1A]">
      {/* Animated Background */}
      <div className="absolute inset-0">
        {/* Gradient Blobs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute top-1/4 -left-1/4 w-96 h-96 bg-[#8B5CF6]/30 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, -90, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-[#2E9BFF]/30 rounded-full blur-[120px]"
        />

        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />
        
        {/* Particles */}
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-[#8B5CF6] rounded-full"
            initial={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
              y: typeof window !== 'undefined' ? window.innerHeight + 20 : 1100,
              opacity: 0,
            }}
            animate={{
              y: -20,
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              delay: Math.random() * 5,
              ease: 'linear',
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-32">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Side - Content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            {/* Social Proof */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex items-center gap-2 mb-6"
            >
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-[#F59E0B] text-[#F59E0B]" />
                ))}
              </div>
              <span className="text-sm text-[#94A3B8]">{landingContent.hero.stats}</span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-5xl lg:text-7xl font-bold mb-6 leading-tight"
            >
              <span className="bg-gradient-to-r from-[#F9FAFB] via-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
                {landingContent.hero.headline}
              </span>
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-xl text-[#94A3B8] mb-10 leading-relaxed max-w-xl"
            >
              {landingContent.hero.subheadline}
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <Link
                href="/login"
                className="group relative px-8 py-4 rounded-xl text-base font-semibold text-white overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] transition-transform group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] opacity-0 group-hover:opacity-100 blur-xl transition-opacity" />
                <span className="relative flex items-center justify-center gap-2">
                  {landingContent.hero.primaryCTA}
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </Link>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.7 }}
              className="mt-12 flex items-center gap-8 text-sm text-[#64748B]"
            >
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[#10B981] rounded-full animate-pulse" />
                <span>All systems operational</span>
              </div>
              <span>•</span>
              <span>Free 14-day trial</span>
              <span>•</span>
              <span>No credit card required</span>
            </motion.div>
          </motion.div>

          {/* Right Side - 3D AI Brain */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="relative h-[600px] hidden lg:block"
          >
            <AIBrain />
            
            {/* Floating Log Elements */}
            <div className="absolute inset-0 pointer-events-none">
              {[
                { text: 'ERROR 500', color: 'text-[#EF4444]', pos: 'top-10 left-10' },
                { text: 'SUCCESS', color: 'text-[#10B981]', pos: 'top-10 right-10' },
                { text: 'WARNING', color: 'text-[#F59E0B]', pos: 'bottom-10 left-10' },
                { text: 'DEBUG', color: 'text-[#2E9BFF]', pos: 'bottom-10 right-10' },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  animate={{
                    y: [0, -20, 0],
                  }}
                  transition={{
                    duration: 3 + i,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: i * 0.5,
                  }}
                  className={`absolute ${item.pos} px-4 py-2 bg-[#1A1F3A]/80 backdrop-blur-sm border border-[#8B5CF6]/30 rounded-lg ${item.color} text-xs font-mono shadow-lg`}
                >
                  {item.text}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

