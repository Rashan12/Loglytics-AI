'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Check, ArrowRight, Sparkles, HelpCircle } from 'lucide-react';
import { LandingNavigation } from '@/components/landing/Navigation';
import { Footer } from '@/components/landing/Footer';
import { landingContent } from '@/lib/landing-content';

export default function PricingPage() {
  const faqs = [
    {
      question: 'What happens when I hit my limits?',
      answer: 'You will receive a notification when you are approaching your limits. You can upgrade to Pro at any time to unlock unlimited access.',
    },
    {
      question: 'Can I change plans anytime?',
      answer: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.',
    },
    {
      question: 'Do you offer discounts for annual billing?',
      answer: 'Yes, we offer a 20% discount when you pay annually. Contact our sales team for more information.',
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and can arrange invoicing for enterprise customers.',
    },
  ];

  return (
    <div className="min-h-screen bg-[#0A0E1A]">
      <LandingNavigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#8B5CF6]/20 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#2E9BFF]/20 rounded-full blur-[120px]" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-block px-4 py-1.5 bg-[#8B5CF6]/10 border border-[#8B5CF6]/30 rounded-full text-[#8B5CF6] text-xs font-semibold uppercase tracking-wider mb-6"
          >
            Pricing
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl lg:text-6xl font-bold text-[#F9FAFB] mb-6"
          >
            Choose the perfect plan
            <br />
            <span className="bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
              for your team
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-[#94A3B8] max-w-2xl mx-auto"
          >
            Start for free, upgrade when you need more power. No hidden fees, cancel anytime.
          </motion.p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Free Tier */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="relative p-8 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-2xl"
            >
              <h3 className="text-2xl font-bold text-[#F9FAFB] mb-2">
                {landingContent.pricing.free.name}
              </h3>
              <p className="text-[#94A3B8] text-sm mb-6">
                {landingContent.pricing.free.description}
              </p>
              <div className="mb-8">
                <span className="text-5xl font-bold text-[#F9FAFB]">
                  {landingContent.pricing.free.price}
                </span>
                <span className="text-[#94A3B8] ml-2">
                  /{landingContent.pricing.free.period}
                </span>
              </div>

              <ul className="space-y-4 mb-8">
                {landingContent.pricing.free.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3 text-[#F9FAFB]">
                    <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href="/login"
                className="block w-full px-6 py-3 text-center rounded-xl border border-[#8B5CF6]/50 text-[#F9FAFB] font-semibold hover:bg-[#8B5CF6]/10 transition-all"
              >
                Get Started Free
              </Link>
            </motion.div>

            {/* Pro Tier */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
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

              <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-2xl blur-xl opacity-30" />

              <div className="relative p-8 bg-[#1A1F3A]/80 backdrop-blur-xl border-2 border-[#8B5CF6]/60 rounded-2xl">
                <h3 className="text-2xl font-bold text-[#F9FAFB] mb-2">
                  {landingContent.pricing.pro.name}
                </h3>
                <p className="text-[#94A3B8] text-sm mb-6">
                  {landingContent.pricing.pro.description}
                </p>
                <div className="mb-8">
                  <span className="text-5xl font-bold bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] bg-clip-text text-transparent">
                    {landingContent.pricing.pro.price}
                  </span>
                  <span className="text-[#94A3B8] ml-2">
                    /{landingContent.pricing.pro.period}
                  </span>
                </div>

                <ul className="space-y-4 mb-8">
                  {landingContent.pricing.pro.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3 text-[#F9FAFB]">
                      <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

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

            {/* Enterprise Tier */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative p-8 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-2xl"
            >
              <h3 className="text-2xl font-bold text-[#F9FAFB] mb-2">
                Enterprise
              </h3>
              <p className="text-[#94A3B8] text-sm mb-6">
                For large organizations with custom needs
              </p>
              <div className="mb-8">
                <span className="text-3xl font-bold text-[#F9FAFB]">
                  Custom Pricing
                </span>
              </div>

              <ul className="space-y-4 mb-8 text-[#F9FAFB]">
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>Everything in Pro</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>Dedicated account manager</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>Custom integrations</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>SLA guarantees</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>On-premise deployment</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
                  <span>Priority support (24/7)</span>
                </li>
              </ul>

              <a
                href="mailto:sales@loglytics.ai"
                className="block w-full px-6 py-3 text-center rounded-xl border border-[#8B5CF6]/50 text-[#F9FAFB] font-semibold hover:bg-[#8B5CF6]/10 transition-all"
              >
                Contact Sales
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="relative py-20">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-[#F9FAFB] mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-[#94A3B8]">
              Everything you need to know about our pricing
            </p>
          </motion.div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="p-6 bg-[#1A1F3A]/60 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-xl"
              >
                <div className="flex items-start gap-4">
                  <HelpCircle className="w-6 h-6 text-[#8B5CF6] flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-[#F9FAFB] mb-2">
                      {faq.question}
                    </h3>
                    <p className="text-[#94A3B8]">{faq.answer}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mt-12"
          >
            <p className="text-[#94A3B8] mb-4">Still have questions?</p>
            <a
              href="mailto:support@loglytics.ai"
              className="inline-flex items-center gap-2 text-[#8B5CF6] hover:text-[#2E9BFF] transition-colors font-semibold"
            >
              Contact our support team
              <ArrowRight className="w-4 h-4" />
            </a>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

