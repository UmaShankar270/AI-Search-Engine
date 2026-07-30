import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
}) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between border-t border-brand-gray-200 dark:border-brand-gray-800 pt-6 mt-4 w-full">
      {/* Page Info */}
      <div className="text-xs text-brand-gray-500 dark:text-brand-gray-400 font-mono">
        Page <span className="font-semibold text-brand-gray-900 dark:text-white">{currentPage}</span> of{' '}
        <span className="font-semibold text-brand-gray-900 dark:text-white">{totalPages}</span>
      </div>

      {/* Control Buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="inline-flex items-center justify-center p-2 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-700 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-sm"
          aria-label="Previous page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="inline-flex items-center justify-center p-2 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-700 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-sm"
          aria-label="Next page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
