'use client';

import { motion } from 'framer-motion';
import { Code, Laptop, Settings, Users } from 'lucide-react';
import { landingContent } from '@/lib/landing-content';

const iconMap = {
  Code,
  Laptop,
  Settings,
  Users,
};

export function UseCases() {
  return (
    <section id="use-cases" className="relative py-32 bg-[#0F1420] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute bottom-0 left-1/4 w-96 h-96 bg-[#2E9BFF]/30 rounded-full blur-[120px]"
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
            Use Cases
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold text-[#F9FAFB] mb-6">
            Built for
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              {' '}modern teams
            </span>
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            From solo developers to enterprise teams, Loglytics AI scales with your needs
          </p>
        </motion.div>

        {/* Use Cases Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {landingContent.useCases.map((useCase, index) => {
            const Icon = iconMap[useCase.icon as keyof typeof iconMap];
            
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="group relative"
              >
                {/* Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/10 to-[#2E9BFF]/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                
                {/* Card */}
                <div className="relative p-8 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-2xl hover:border-[#8B5CF6]/60 transition-all">
                  {/* Icon */}
                  <div className="w-16 h-16 mb-6 bg-gradient-to-br from-[#8B5CF6]/20 to-[#2E9BFF]/20 border border-[#8B5CF6]/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="w-8 h-8 text-[#8B5CF6]" />
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold text-[#F9FAFB] mb-4">
                    {useCase.title}
                  </h3>
                  <p className="text-[#94A3B8] leading-relaxed">
                    {useCase.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

