import React, { useState } from 'react';
import { RefreshCw, X, Link, Check, ExternalLink } from 'lucide-react';

export default function ComparisonActions({
  repoA,
  repoB,
  onSwap,
  onClear,
}) {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    if (!repoA || !repoB) return;
    const url = `${window.location.origin}/compare?a=${repoA.name.toLowerCase()}&b=${repoB.name.toLowerCase()}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className="flex flex-wrap gap-3 items-center justify-between border-t border-brand-gray-200 dark:border-brand-gray-800 pt-4 w-full text-xs">
      <div className="flex items-center space-x-2">
        {/* Swap button */}
        <button
          onClick={onSwap}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-lg hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 font-semibold transition-colors cursor-pointer text-brand-gray-700 dark:text-brand-gray-300"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Swap Positions</span>
        </button>

        {/* Copy Comparison Link */}
        <button
          onClick={handleCopyLink}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-lg hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 font-semibold transition-colors cursor-pointer text-brand-gray-700 dark:text-brand-gray-300"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-500">Copied Link!</span>
            </>
          ) : (
            <>
              <Link className="w-3.5 h-3.5" />
              <span>Copy Comparison Link</span>
            </>
          )}
        </button>
      </div>

      {/* Clear Button */}
      <button
        onClick={onClear}
        className="inline-flex items-center space-x-1.5 px-3.5 py-2 border border-red-200/60 dark:border-red-900/60 bg-red-50/50 dark:bg-red-955/20 text-red-600 rounded-lg hover:bg-red-100 font-semibold transition-colors cursor-pointer"
      >
        <X className="w-3.5 h-3.5" />
        <span>Clear Comparison</span>
      </button>
    </div>
  );
}
