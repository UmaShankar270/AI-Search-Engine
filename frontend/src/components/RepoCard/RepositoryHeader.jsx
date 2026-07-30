import React, { useState } from 'react';
import { Star, GitFork, Info, Calendar, Bookmark, GitCompare, ExternalLink, Shield } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function RepositoryHeader({ details }) {
  const { compareRepos, addRepoToCompare, removeRepoFromCompare } = useApp();
  const [bookmarked, setBookmarked] = useState(false);

  const isComparing = compareRepos.some((r) => r.id === details.id);
  const compareCount = compareRepos.length;

  const handleCompareToggle = () => {
    if (isComparing) {
      removeRepoFromCompare(details.id);
    } else {
      addRepoToCompare(details);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 md:p-8 shadow-sm text-left space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5 truncate">
          <img
            src={details.avatar}
            alt={`${details.owner} avatar`}
            className="w-12 h-12 rounded-xl object-cover border border-brand-gray-200 dark:border-brand-gray-800 flex-shrink-0"
          />
          <div className="truncate">
            <div className="flex items-center space-x-1.5 text-xs text-brand-gray-400 dark:text-brand-gray-500 font-mono">
              <span>github.com</span>
              <span>/</span>
              <span>{details.owner}</span>
            </div>
            <h1 className="text-xl md:text-3xl font-extrabold text-brand-gray-955 dark:text-white truncate tracking-tight">
              {details.name}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setBookmarked(!bookmarked)}
            className={`p-2.5 rounded-lg border text-xs font-semibold transition-colors cursor-pointer ${
              bookmarked
                ? 'text-yellow-600 border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20'
                : 'text-brand-gray-600 border-brand-gray-200 dark:border-brand-gray-800 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850'
            }`}
            aria-label="Bookmark repository"
          >
            <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
          </button>

          <button
            onClick={handleCompareToggle}
            disabled={!isComparing && compareCount >= 2}
            className={`inline-flex items-center space-x-1.5 px-4 py-2 border text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
              isComparing
                ? 'text-red-600 border-red-200 bg-red-50 dark:bg-red-955/20 hover:bg-red-100'
                : compareCount >= 2
                ? 'text-brand-gray-300 border-brand-gray-100 cursor-not-allowed dark:border-brand-gray-900'
                : 'text-brand-gray-700 border-brand-gray-200 dark:border-brand-gray-800 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850'
            }`}
          >
            <GitCompare className="w-4 h-4" />
            <span>{isComparing ? 'Remove Compare' : 'Compare'}</span>
          </button>

          <a
            href={`https://github.com/${details.owner}/${details.name}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 px-4 py-2 bg-brand-gray-950 dark:bg-white text-white dark:text-black hover:bg-brand-gray-800 dark:hover:bg-brand-gray-100 text-xs font-semibold rounded-lg transition-colors cursor-pointer shadow-sm"
          >
            <span>GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      <p className="text-sm md:text-base text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed max-w-3xl">
        {details.description}
      </p>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 pt-3 border-t border-brand-gray-100 dark:border-brand-gray-800/60 text-xs text-brand-gray-405 dark:text-brand-gray-500">
        <div className="flex items-center space-x-1.5">
          <Star className="w-4 h-4 text-yellow-500 fill-current" />
          <span className="text-brand-gray-700 dark:text-brand-gray-300 font-bold">{details.stars?.toLocaleString()}</span>
          <span>stars</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <GitFork className="w-4 h-4 text-accent-blue-500" />
          <span className="text-brand-gray-700 dark:text-brand-gray-300 font-bold">{details.forks?.toLocaleString()}</span>
          <span>forks</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Info className="w-4 h-4 text-red-500" />
          <span className="text-brand-gray-700 dark:text-brand-gray-300 font-bold">{details.openIssues}</span>
          <span>open issues</span>
        </div>
        {details.license && (
          <div className="flex items-center space-x-1.5">
            <Shield className="w-4 h-4 text-indigo-500" />
            <span className="text-brand-gray-700 dark:text-brand-gray-300 font-bold">{details.license}</span>
          </div>
        )}
        <div className="flex items-center space-x-1.5 ml-auto text-[10px]">
          <Calendar className="w-3.5 h-3.5" />
          <span>Last updated {formatDate(details.lastUpdated)}</span>
        </div>
      </div>
    </div>
  );
}
