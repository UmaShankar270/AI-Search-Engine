import React from 'react';
import { FaGithub, FaTwitter, FaGlobe, FaHeart } from 'react-icons/fa';

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-950 text-brand-gray-500 dark:text-brand-gray-400 py-8 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          {/* Left copyright and brand info */}
          <div className="flex items-center space-x-2 text-sm">
            <span className="font-semibold text-brand-gray-900 dark:text-white">GitPulse</span>
            <span>&copy; {new Date().getFullYear()}</span>
            <span>&middot;</span>
            <span className="flex items-center">
              Built for Hackathon with <FaHeart className="w-3.5 h-3.5 text-red-500 mx-1 fill-current" />
            </span>
          </div>

          {/* Center disclaimer */}
          <div className="text-xs text-center text-brand-gray-400 dark:text-brand-gray-600 max-w-md">
            This platform uses semantic AI structures to discover and compare repositories. API responses are ready for FastAPI backend ingestion.
          </div>

          {/* Right social media links */}
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white transition-colors"
              aria-label="GitHub Repository"
            >
              <FaGithub className="w-5 h-5" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white transition-colors"
              aria-label="Twitter Page"
            >
              <FaTwitter className="w-5 h-5" />
            </a>
            <a
              href="https://vercel.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white transition-colors"
              aria-label="Vercel Website"
            >
              <FaGlobe className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
