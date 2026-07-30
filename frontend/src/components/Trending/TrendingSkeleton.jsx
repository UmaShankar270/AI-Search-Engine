import React from 'react';

export function TrendingSkeletonCard() {
  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 space-y-4 animate-pulse text-left">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 w-2/3">
          <div className="w-8 h-8 rounded-lg bg-brand-gray-200 dark:bg-brand-gray-850 flex-shrink-0" />
          <div className="space-y-1.5 w-full">
            <div className="h-4 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-1/3" />
            <div className="h-3 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-1/2" />
          </div>
        </div>
        <div className="h-5 bg-brand-gray-200 dark:bg-brand-gray-850 rounded-full w-16" />
      </div>
      <div className="space-y-2">
        <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-full" />
        <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-5/6" />
      </div>
      <div className="flex flex-wrap gap-1.5 pt-1">
        <div className="h-4 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-12" />
        <div className="h-4 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-16" />
      </div>
      <div className="flex items-center justify-between pt-4 border-t border-brand-gray-100 dark:border-brand-gray-800/60 mt-2">
        <div className="flex items-center space-x-4 w-1/2">
          <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-10" />
          <div className="h-3.5 bg-brand-gray-200 dark:bg-brand-gray-850 rounded w-12" />
        </div>
        <div className="h-7 bg-brand-gray-200 dark:bg-brand-gray-850 rounded-lg w-16" />
      </div>
    </div>
  );
}

export default function TrendingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
      <TrendingSkeletonCard />
      <TrendingSkeletonCard />
      <TrendingSkeletonCard />
      <TrendingSkeletonCard />
    </div>
  );
}
