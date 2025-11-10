'use client';

import { motion } from 'framer-motion';
import { landingContent } from '@/lib/landing-content';
import { Cloud, Container, GitBranch, Workflow } from 'lucide-react';

const logoMap: Record<string, any> = {
  aws: Cloud,
  azure: Cloud,
  gcp: Cloud,
  docker: Container,
  kubernetes: Container,
  github: GitBranch,
  gitlab: GitBranch,
  jenkins: Workflow,
};

export function Integrations() {
  return (
    <section id="integrations" className="relative py-32 bg-[#0A0E1A] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(139,92,246,0.1),transparent_50%)]" />

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
            Integrations
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold text-[#F9FAFB] mb-6">
            Works with
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              {' '}your stack
            </span>
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Seamlessly integrate with your favorite cloud providers, containers, and CI/CD tools
          </p>
        </motion.div>

        {/* Integration Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
          {landingContent.integrations.map((integration, index) => {
            const Logo = logoMap[integration.logo];
            
            return (
              <motion.div
                key={integration.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                whileHover={{ y: -10, scale: 1.05 }}
                className="group relative"
              >
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/20 to-[#2E9BFF]/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Card */}
                <div className="relative h-32 bg-[#1A1F3A]/60 backdrop-blur-sm border border-[#8B5CF6]/30 rounded-2xl flex flex-col items-center justify-center gap-3 hover:border-[#8B5CF6]/60 transition-all">
                  <Logo className="w-10 h-10 text-[#8B5CF6] group-hover:text-[#2E9BFF] transition-colors" />
                  <span className="text-sm font-semibold text-[#F9FAFB]">
                    {integration.name}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* More Integrations Link */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center"
        >
          <p className="text-[#94A3B8]">
            + 20 more integrations and counting
          </p>
        </motion.div>
      </div>
    </section>
  );
}

