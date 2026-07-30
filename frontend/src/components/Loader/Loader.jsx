import React from 'react';
import { Loader2 } from 'lucide-react';

export function Spinner({ size = 'medium', className = '' }) {
  const sizes = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <Loader2
      className={`animate-spin text-accent-blue-500 ${sizes[size]} ${className}`}
      aria-label="Loading content"
    />
  );
}

export function PageLoader() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-[50vh]">
      <Spinner size="large" />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 space-y-4 animate-pulse text-left w-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 w-2/3">
          <div className="w-8 h-8 rounded-lg bg-brand-gray-200 dark:bg-brand-gray-800 flex-shrink-0" />
          <div className="space-y-1.5 w-full">
            <div className="h-4 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-1/3" />
            <div className="h-3 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-1/2" />
          </div>
        </div>
        <div className="h-5 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-full w-14" />
      </div>
      <div className="space-y-2">
        <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-full" />
        <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-5/6" />
      </div>
      <div className="flex flex-wrap gap-1.5 pt-1">
        <div className="h-5 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-12" />
        <div className="h-5 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-16" />
      </div>
      <div className="flex items-center justify-between pt-4 border-t border-brand-gray-100 dark:border-brand-gray-800/60 mt-2">
        <div className="h-3 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-1/4" />
        <div className="h-7 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-lg w-16" />
      </div>
    </div>
  );
}

export function SkeletonDetails() {
  return (
    <div className="space-y-6 w-full text-left animate-pulse">
      <div className="h-6 bg-brand-gray-200 dark:bg-brand-gray-800 rounded w-24" />
      <div className="h-44 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-2xl w-full" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-96 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-2xl" />
        <div className="h-96 bg-brand-gray-200 dark:bg-brand-gray-800 rounded-2xl" />
      </div>
    </div>
  );
}
