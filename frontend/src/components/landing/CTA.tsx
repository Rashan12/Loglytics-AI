'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

export function CTA() {
  return (
    <section className="relative py-32 bg-[#0A0E1A] overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        {/* Large Gradient Blob */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-full blur-[150px]"
        />

        {/* Floating Particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-[#8B5CF6] rounded-full"
            initial={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1080,
              opacity: 0,
            }}
            animate={{
              y: typeof window !== 'undefined' 
                ? [null, window.innerHeight + Math.random() * -100]
                : [null, 1080 + Math.random() * -100],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 5 + 5,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 lg:px-8 text-center">
        {/* Sparkle Icon */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          whileInView={{ scale: 1, rotate: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, type: 'spring' }}
          className="inline-block mb-8"
        >
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-full blur-2xl opacity-50 animate-pulse" />
            <div className="relative w-20 h-20 bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-2xl flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
          </div>
        </motion.div>

        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl lg:text-6xl font-bold text-[#F9FAFB] mb-6"
        >
          Ready to revolutionize
          <br />
          <span className="bg-gradient-to-r from-[#8B5CF6] via-[#2E9BFF] to-[#10B981] bg-clip-text text-transparent">
            your log management?
          </span>
        </motion.h2>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-xl lg:text-2xl text-[#94A3B8] mb-12 max-w-3xl mx-auto"
        >
          Start analyzing your logs with AI in under 5 minutes.
          <br />
          No credit card required.
        </motion.p>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Link
            href="/login"
            className="group relative inline-flex items-center gap-3 px-10 py-5 rounded-2xl text-lg font-bold text-white overflow-hidden"
          >
            {/* Button Background */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] transition-transform group-hover:scale-110" />
            
            {/* Button Glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] opacity-0 group-hover:opacity-100 blur-2xl transition-opacity" />
            
            {/* Button Content */}
            <span className="relative">Sign Up Now - It's Free</span>
            <ArrowRight className="relative w-6 h-6 group-hover:translate-x-2 transition-transform" />
          </Link>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-6 text-sm text-[#94A3B8]"
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-[#10B981] rounded-full" />
            <span>Free forever plan</span>
          </div>
          <span className="hidden sm:block">•</span>
          <span>No credit card required</span>
          <span className="hidden sm:block">•</span>
          <span>Cancel anytime</span>
        </motion.div>
      </div>
    </section>
  );
}

