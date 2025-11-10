'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { Menu, X, ChevronDown } from 'lucide-react';

export function LandingNavigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProductDropdownOpen, setIsProductDropdownOpen] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isProductDropdownOpen) return;
    
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.product-dropdown-container')) {
        setIsProductDropdownOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isProductDropdownOpen]);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-[#0A0E1A]/80 backdrop-blur-xl border-b border-[#8B5CF6]/20 shadow-lg' 
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative w-10 h-10 bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">L</span>
              </div>
            </div>
            <span className="text-xl font-bold text-[#F9FAFB]">Loglytics AI</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-8">
            {/* Product Dropdown */}
            <div className="relative product-dropdown-container">
              <button
                onClick={() => setIsProductDropdownOpen(!isProductDropdownOpen)}
                className="flex items-center gap-1 text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium"
              >
                Product
                <ChevronDown className={`w-4 h-4 transition-transform ${isProductDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              <AnimatePresence>
                {isProductDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full left-0 mt-2 w-56 bg-[#1A1F3A]/95 backdrop-blur-xl border border-[#8B5CF6]/30 rounded-xl shadow-2xl overflow-hidden"
                  >
                    <Link 
                      href="#features" 
                      onClick={() => setIsProductDropdownOpen(false)}
                      className="block px-4 py-3 text-sm text-[#F9FAFB] hover:bg-[#8B5CF6]/10 transition-colors"
                    >
                      Features
                    </Link>
                    <Link 
                      href="#integrations" 
                      onClick={() => setIsProductDropdownOpen(false)}
                      className="block px-4 py-3 text-sm text-[#F9FAFB] hover:bg-[#8B5CF6]/10 transition-colors"
                    >
                      Integrations
                    </Link>
                    <Link 
                      href="#use-cases" 
                      onClick={() => setIsProductDropdownOpen(false)}
                      className="block px-4 py-3 text-sm text-[#F9FAFB] hover:bg-[#8B5CF6]/10 transition-colors"
                    >
                      Use Cases
                    </Link>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <Link href="/pricing" className="text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
              Pricing
            </Link>
            <Link href="#docs" className="text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
              Docs
            </Link>
            <Link href="#blog" className="text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
              Blog
            </Link>
            <Link href="#about" className="text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
              About
            </Link>
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex items-center gap-4">
            <Link
              href="/login"
              className="text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="relative px-6 py-2.5 rounded-lg text-sm font-semibold text-white overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] transition-transform group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] opacity-0 group-hover:opacity-100 blur-xl transition-opacity" />
              <span className="relative">Sign Up Now</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden text-[#F9FAFB] p-2"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-[#0A0E1A]/95 backdrop-blur-xl border-t border-[#8B5CF6]/20"
          >
            <div className="px-6 py-4 space-y-4">
              <Link href="#features" className="block text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
                Features
              </Link>
              <Link href="/pricing" className="block text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
                Pricing
              </Link>
              <Link href="#docs" className="block text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
                Docs
              </Link>
              <Link href="#blog" className="block text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
                Blog
              </Link>
              <Link href="#about" className="block text-[#F9FAFB] hover:text-[#8B5CF6] transition-colors text-sm font-medium">
                About
              </Link>
              <div className="pt-4 border-t border-[#8B5CF6]/20 space-y-3">
                <Link
                  href="/login"
                  className="block text-center px-6 py-2.5 rounded-lg text-sm font-medium text-[#F9FAFB] border border-[#8B5CF6]/50 hover:bg-[#8B5CF6]/10 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/login"
                  className="block text-center px-6 py-2.5 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF]"
                >
                  Sign Up Now
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

