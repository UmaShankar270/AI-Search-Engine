import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 flex-1 flex flex-col items-center justify-center text-center">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-brand-gray-100 dark:bg-brand-gray-900 text-brand-gray-700 dark:text-brand-gray-300 mb-6">
        <HelpCircle className="w-8 h-8" />
      </div>
      <h1 className="text-4xl font-extrabold text-brand-gray-900 dark:text-white mb-2 tracking-tight">
        404 - Page Not Found
      </h1>
      <p className="text-base text-brand-gray-500 dark:text-brand-gray-400 mb-8 max-w-sm leading-relaxed">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        to="/"
        className="flex items-center space-x-2 px-5 py-2.5 text-sm font-medium text-white bg-brand-gray-900 dark:bg-white dark:text-black rounded-lg hover:bg-brand-gray-800 dark:hover:bg-brand-gray-100 transition-colors shadow-sm focus:outline-none"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Discover</span>
      </Link>
    </div>
  );
}
