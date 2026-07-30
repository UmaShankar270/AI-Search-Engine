import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Terminal, GitBranch, Zap } from 'lucide-react';
import ThemeToggle from '../ThemeToggle/ThemeToggle';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { name: 'Discover', path: '/' },
    { name: 'Trending', path: '/trending' },
    { name: 'Compare', path: '/compare' },
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-brand-gray-200 dark:border-brand-gray-800 bg-white/70 dark:bg-brand-gray-950/70 backdrop-blur-md glass-effect">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 text-brand-gray-900 dark:text-white font-bold text-lg tracking-tight">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-black dark:bg-white text-white dark:text-black">
                <Zap className="w-5 h-5 fill-current" />
              </div>
              <span className="bg-gradient-to-r from-brand-gray-900 via-brand-gray-700 to-brand-gray-900 dark:from-white dark:via-brand-gray-300 dark:to-white bg-clip-text text-transparent">
                GitPulse
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer ${
                  isActive(item.path)
                    ? 'text-brand-gray-900 dark:text-white bg-brand-gray-100 dark:bg-brand-gray-900'
                    : 'text-brand-gray-500 dark:text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white'
                }`}
              >
                {item.name}
              </Link>
            ))}
            <div className="pl-4 border-l border-brand-gray-200 dark:border-brand-gray-800 ml-4">
              <ThemeToggle />
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-brand-gray-500 hover:text-brand-gray-900 dark:hover:text-white focus:outline-none cursor-pointer"
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isOpen && (
        <div className="md:hidden border-t border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-950 px-2 pt-2 pb-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                isActive(item.path)
                  ? 'text-brand-gray-900 dark:text-white bg-brand-gray-100 dark:bg-brand-gray-900'
                  : 'text-brand-gray-500 dark:text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white'
              }`}
            >
              {item.name}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
