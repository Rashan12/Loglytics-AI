'use client';

import { motion } from 'framer-motion';
import {
  MessageSquare,
  Search,
  BarChart3,
  Zap,
  Cloud,
  Target,
} from 'lucide-react';
import { landingContent } from '@/lib/landing-content';

const iconMap = {
  MessageSquare,
  Search,
  BarChart3,
  Zap,
  Cloud,
  Target,
};

export function Features() {
  return (
    <section id="features" className="relative py-32 bg-[#0A0E1A] overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute top-0 right-1/4 w-96 h-96 bg-[#8B5CF6]/20 rounded-full blur-[100px]"
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
            Features
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold text-[#F9FAFB] mb-6">
            Everything you need to
            <br />
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              monitor logs intelligently
            </span>
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-3xl mx-auto">
            Powerful features that transform how you handle logs, from real-time monitoring to AI-powered insights
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {landingContent.features.map((feature, index) => {
            const Icon = iconMap[feature.icon as keyof typeof iconMap];
            
            return (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -10 }}
                className="group relative"
              >
                {/* Card Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6]/0 via-[#8B5CF6]/10 to-[#2E9BFF]/0 rounded-2xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />
                
                {/* Card */}
                <div className="relative h-full p-8 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-2xl hover:border-[#8B5CF6]/60 transition-all duration-300">
                  {/* Icon */}
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className="w-14 h-14 mb-6 bg-gradient-to-br from-[#8B5CF6]/20 to-[#2E9BFF]/20 border border-[#8B5CF6]/30 rounded-xl flex items-center justify-center"
                  >
                    <Icon className="w-7 h-7 text-[#8B5CF6]" />
                  </motion.div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-[#F9FAFB] mb-3 group-hover:text-[#8B5CF6] transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-[#94A3B8] leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Hover Indicator */}
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: '100%' }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 + 0.5 }}
                    className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-full"
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

