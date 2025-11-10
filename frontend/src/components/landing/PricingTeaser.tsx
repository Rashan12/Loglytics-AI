'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Check, Sparkles, ArrowRight } from 'lucide-react';
import { landingContent } from '@/lib/landing-content';

export function PricingTeaser() {
  return (
    <section className="relative py-32 bg-[#0A0E1A] overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.1),transparent_70%)]" />
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 180, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-[#8B5CF6]/20 to-[#2E9BFF]/20 rounded-full blur-[100px]"
        />
      </div>

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
            Pricing
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold text-[#F9FAFB] mb-6">
            Simple,
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              {' '}transparent pricing
            </span>
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Start for free, upgrade when you need more power
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-12">
          {/* Free Tier */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="h-full p-8 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-2xl">
              {/* Header */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-[#F9FAFB] mb-2">
                  {landingContent.pricing.free.name}
                </h3>
                <p className="text-[#94A3B8] text-sm mb-4">
                  {landingContent.pricing.free.description}
                </p>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-[#F9FAFB]">
                    {landingContent.pricing.free.price}
                  </span>
                  <span className="text-[#94A3B8]">
                    /{landingContent.pricing.free.period}
                  </span>
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {landingContent.pricing.free.features.map((feature, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center gap-3 text-[#F9FAFB]"
                  >
                    <Check className="w-5 h-5 text-[#10B981] flex-shrink-0" />
                    <span>{feature}</span>
                  </motion.li>
                ))}
              </ul>

              {/* CTA */}
              <Link
                href="/login"
                className="block w-full px-6 py-3 text-center rounded-xl border border-[#8B5CF6]/50 text-[#F9FAFB] font-semibold hover:bg-[#8B5CF6]/10 transition-all"
              >
                Get Started Free
              </Link>
            </div>
          </motion.div>

          {/* Pro Tier */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="relative"
          >
            {/* Popular Badge */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
              <div className="px-4 py-1.5 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-full text-white text-xs font-semibold flex items-center gap-2">
                <Sparkles className="w-3 h-3" />
                POPULAR
              </div>
            </div>

            {/* Glow Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-2xl blur-xl opacity-30" />

            <div className="relative h-full p-8 bg-[#1A1F3A]/80 backdrop-blur-xl border-2 border-[#8B5CF6]/60 rounded-2xl">
              {/* Header */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-[#F9FAFB] mb-2">
                  {landingContent.pricing.pro.name}
                </h3>
                <p className="text-[#94A3B8] text-sm mb-4">
                  {landingContent.pricing.pro.description}
                </p>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
                    {landingContent.pricing.pro.price}
                  </span>
                  <span className="text-[#94A3B8]">
                    /{landingContent.pricing.pro.period}
                  </span>
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {landingContent.pricing.pro.features.map((feature, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center gap-3 text-[#F9FAFB]"
                  >
                    <Check className="w-5 h-5 text-[#10B981] flex-shrink-0" />
                    <span>{feature}</span>
                  </motion.li>
                ))}
              </ul>

              {/* CTA */}
              <Link
                href="/login"
                className="group relative block w-full px-6 py-3 rounded-xl text-center font-semibold text-white overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] transition-transform group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] opacity-0 group-hover:opacity-100 blur-xl transition-opacity" />
                <span className="relative">Get Started</span>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* View Full Pricing Link */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center"
        >
          <Link
            href="/pricing"
            className="inline-flex items-center gap-2 text-[#8B5CF6] hover:text-[#2E9BFF] transition-colors font-semibold"
          >
            View Full Pricing Details
            <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

