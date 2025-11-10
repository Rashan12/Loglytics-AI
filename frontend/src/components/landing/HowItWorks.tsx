'use client';

import { motion } from 'framer-motion';
import { landingContent } from '@/lib/landing-content';
import { Plug, Brain, Bell, MessageSquare } from 'lucide-react';

const stepIcons = [Plug, Brain, Bell, MessageSquare];

export function HowItWorks() {
  return (
    <section className="relative py-32 bg-[#0F1420] overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-block px-4 py-1.5 bg-[#8B5CF6]/10 border border-[#8B5CF6]/30 rounded-full text-[#8B5CF6] text-xs font-semibold uppercase tracking-wider mb-6"
          >
            How It Works
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold text-[#F9FAFB] mb-6">
            Get started in
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              {' '}minutes
            </span>
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Four simple steps to transform your log management workflow
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Connection Line */}
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5, ease: 'easeInOut' }}
            className="absolute top-12 left-0 right-0 h-1 bg-gradient-to-r from-[#8B5CF6] via-[#2E9BFF] to-[#10B981] origin-left hidden lg:block"
          />

          {/* Steps */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
            {landingContent.howItWorks.map((step, index) => {
              const Icon = stepIcons[index];
              
              return (
                <motion.div
                  key={step.step}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className="relative"
                >
                  {/* Step Number Circle */}
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.2 + 0.3 }}
                    className="relative w-24 h-24 mx-auto mb-6"
                  >
                    {/* Glow */}
                    <div className="absolute inset-0 bg-[#8B5CF6] rounded-full blur-2xl opacity-30 animate-pulse" />
                    
                    {/* Circle */}
                    <div className="relative w-full h-full bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-full flex items-center justify-center border-4 border-[#0F1420]">
                      <Icon className="w-10 h-10 text-white" />
                    </div>

                    {/* Step Number Badge */}
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-[#F9FAFB] rounded-full flex items-center justify-center text-[#0F1420] font-bold text-sm border-4 border-[#0F1420]">
                      {step.step}
                    </div>
                  </motion.div>

                  {/* Content */}
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-[#F9FAFB] mb-3">
                      {step.title}
                    </h3>
                    <p className="text-[#94A3B8]">
                      {step.description}
                    </p>
                  </div>

                  {/* Arrow (desktop only) */}
                  {index < landingContent.howItWorks.length - 1 && (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: index * 0.2 + 0.6 }}
                      className="hidden lg:block absolute top-12 -right-4 text-[#8B5CF6]"
                    >
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-16"
        >
          <p className="text-[#94A3B8] mb-6">
            Ready to transform your log management?
          </p>
          <motion.a
            href="/login"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-block px-8 py-4 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-xl text-white font-semibold shadow-lg shadow-[#8B5CF6]/50 hover:shadow-xl hover:shadow-[#8B5CF6]/60 transition-all"
          >
            Get Started Free
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}

