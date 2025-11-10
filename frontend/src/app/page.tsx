import { LandingNavigation } from '@/components/landing/Navigation';
import { Hero } from '@/components/landing/Hero';
import { Features } from '@/components/landing/Features';
import { HowItWorks } from '@/components/landing/HowItWorks';
import { Integrations } from '@/components/landing/Integrations';
import { UseCases } from '@/components/landing/UseCases';
import { PricingTeaser } from '@/components/landing/PricingTeaser';
import { CTA } from '@/components/landing/CTA';
import { Footer } from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <main className="relative bg-[#0A0E1A] overflow-hidden">
      <LandingNavigation />
      <Hero />
      <Features />
      <HowItWorks />
      <Integrations />
      <UseCases />
      <PricingTeaser />
      <CTA />
      <Footer />
    </main>
  );
}
