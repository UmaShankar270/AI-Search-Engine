import React, { useState } from 'react';
import { ExternalLink, GitCompare, Link, Share2, Check } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function ActionButtons({ details }) {
  const { compareRepos, addRepoToCompare, removeRepoFromCompare } = useApp();
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);

  const isComparing = compareRepos.some((r) => r.id === details.id);
  const compareCount = compareRepos.length;

  const handleCompareToggle = () => {
    if (isComparing) {
      removeRepoFromCompare(details.id);
    } else {
      addRepoToCompare(details);
    }
  };

  const handleCopyUrl = async () => {
    const url = `https://github.com/${details.owner}/${details.name}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleShareClick = () => {
    setShared(true);
    setTimeout(() => setShared(false), 2000);
  };

  return (
    <div className="flex flex-wrap gap-3 items-center justify-start w-full">
      {/* GitHub Link */}
      <a
        href={`https://github.com/${details.owner}/${details.name}`}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-brand-gray-950 dark:bg-white text-white dark:text-black hover:bg-brand-gray-800 dark:hover:bg-brand-gray-100 transition-colors shadow-sm cursor-pointer"
      >
        <span>Open on GitHub</span>
        <ExternalLink className="w-4 h-4" />
      </a>

      {/* Compare Button */}
      <button
        onClick={handleCompareToggle}
        disabled={!isComparing && compareCount >= 2}
        className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors cursor-pointer ${
          isComparing
            ? 'text-red-600 border-red-200 bg-red-50 dark:bg-red-950/20 hover:bg-red-100'
            : compareCount >= 2
            ? 'text-brand-gray-300 border-brand-gray-150 cursor-not-allowed dark:border-brand-gray-900'
            : 'text-brand-gray-700 border-brand-gray-200 dark:border-brand-gray-850 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-800 text-brand-gray-800 dark:text-brand-gray-300'
        }`}
      >
        <GitCompare className="w-4 h-4" />
        <span>{isComparing ? 'Remove from Compare' : 'Compare Repository'}</span>
      </button>

      {/* Copy URL Button */}
      <button
        onClick={handleCopyUrl}
        className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-750 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 transition-colors cursor-pointer"
      >
        {copied ? (
          <>
            <Check className="w-4 h-4 text-emerald-500" />
            <span className="text-emerald-500">Copied Link!</span>
          </>
        ) : (
          <>
            <Link className="w-4 h-4" />
            <span>Copy Repo URL</span>
          </>
        )}
      </button>

      {/* Share Button (UI only) */}
      <button
        onClick={handleShareClick}
        className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-750 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 transition-colors cursor-pointer"
      >
        {shared ? (
          <>
            <Check className="w-4 h-4 text-emerald-500" />
            <span className="text-emerald-500">Shared!</span>
          </>
        ) : (
          <>
            <Share2 className="w-4 h-4" />
            <span>Share</span>
          </>
        )}
      </button>
    </div>
  );
}
