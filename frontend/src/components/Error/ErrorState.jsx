import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, RefreshCw, ArrowLeft, Home } from 'lucide-react';

export default function ErrorState({
  title = 'An unexpected error occurred',
  message = 'We encountered an error while processing your request. Please try again or return home.',
  onRetry,
}) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 border border-brand-gray-250 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl text-center max-w-lg mx-auto shadow-sm w-full my-8">
      {/* Icon */}
      <div className="p-4 bg-red-50 dark:bg-red-955/20 border border-red-105 dark:border-red-900/50 rounded-2xl mb-4 text-red-500">
        <AlertCircle className="w-12 h-12" />
      </div>

      {/* Header */}
      <h3 className="text-xl font-extrabold text-brand-gray-955 dark:text-white mb-2 tracking-tight">
        {title}
      </h3>

      {/* Subtext */}
      <p className="text-sm text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed mb-8">
        {message}
      </p>

      {/* Actions */}
      <div className="flex flex-wrap items-center justify-center gap-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center space-x-2 px-4.5 py-2.5 bg-brand-gray-955 dark:bg-white text-white dark:text-black hover:bg-brand-gray-800 dark:hover:bg-brand-gray-100 text-xs font-semibold rounded-lg transition-colors cursor-pointer shadow-sm focus-visible:ring-2 focus-visible:ring-offset-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Operation</span>
          </button>
        )}

        <Link
          to="/"
          className="inline-flex items-center space-x-2 px-4.5 py-2.5 border border-brand-gray-205 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-950 text-xs font-semibold text-brand-gray-700 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-900 rounded-lg transition-colors shadow-sm focus-visible:ring-2"
        >
          <Home className="w-3.5 h-3.5" />
          <span>Go Home</span>
        </Link>

        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-brand-gray-405 hover:text-brand-gray-950 dark:hover:text-white transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Go Back</span>
        </button>
      </div>
    </div>
  );
}
