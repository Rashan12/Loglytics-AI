'use client';

import Link from 'next/link';
import { Github, Twitter, Linkedin, Mail } from 'lucide-react';
import { landingContent } from '@/lib/landing-content';

export function Footer() {
  return (
    <footer className="relative bg-[#0A0E1A] border-t border-[#8B5CF6]/20">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">L</span>
              </div>
              <span className="text-xl font-bold text-[#F9FAFB]">Loglytics AI</span>
            </Link>
            <p className="text-[#94A3B8] mb-6 max-w-sm">
              AI-powered log analysis platform that transforms log chaos into clear insights.
            </p>
            
            {/* Social Links */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-[#1A1F3A] border border-[#8B5CF6]/30 flex items-center justify-center text-[#94A3B8] hover:text-[#8B5CF6] hover:border-[#8B5CF6]/60 transition-all"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-[#1A1F3A] border border-[#8B5CF6]/30 flex items-center justify-center text-[#94A3B8] hover:text-[#8B5CF6] hover:border-[#8B5CF6]/60 transition-all"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-[#1A1F3A] border border-[#8B5CF6]/30 flex items-center justify-center text-[#94A3B8] hover:text-[#8B5CF6] hover:border-[#8B5CF6]/60 transition-all"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="mailto:contact@loglytics.ai"
                className="w-10 h-10 rounded-lg bg-[#1A1F3A] border border-[#8B5CF6]/30 flex items-center justify-center text-[#94A3B8] hover:text-[#8B5CF6] hover:border-[#8B5CF6]/60 transition-all"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-[#F9FAFB] font-semibold mb-4">Product</h3>
            <ul className="space-y-3">
              {landingContent.footer.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-[#94A3B8] hover:text-[#8B5CF6] transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-[#F9FAFB] font-semibold mb-4">Company</h3>
            <ul className="space-y-3">
              {landingContent.footer.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-[#94A3B8] hover:text-[#8B5CF6] transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources & Legal */}
          <div>
            <h3 className="text-[#F9FAFB] font-semibold mb-4">Resources</h3>
            <ul className="space-y-3 mb-6">
              {landingContent.footer.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-[#94A3B8] hover:text-[#8B5CF6] transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>

            <h3 className="text-[#F9FAFB] font-semibold mb-4">Legal</h3>
            <ul className="space-y-3">
              {landingContent.footer.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-[#94A3B8] hover:text-[#8B5CF6] transition-colors text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-[#8B5CF6]/20">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-[#64748B] text-sm">
              © {new Date().getFullYear()} Loglytics AI. All rights reserved.
            </p>
            <p className="text-[#64748B] text-sm">
              Built with ❤️ for developers everywhere
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

