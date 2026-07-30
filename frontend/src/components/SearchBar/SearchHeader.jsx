import React from 'react';
import SearchBar from './SearchBar';
import { Sparkles, Activity } from 'lucide-react';

export default function SearchHeader({
  query,
  setQuery,
  onSearch,
  totalResults,
  executionTime = 0.12,
  hasSearched,
}) {
  return (
    <div className="w-full space-y-6">
      <div className="w-full">
        <SearchBar value={query} onChange={setQuery} onSubmit={onSearch} />
      </div>

      {hasSearched && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-brand-gray-100 dark:border-brand-gray-800/60 pb-4 gap-2 text-left">
          <div className="space-y-1">
            <h2 className="text-xl font-extrabold text-brand-gray-955 dark:text-white flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-accent-blue-500" />
              <span>Semantic Discoveries</span>
            </h2>
            <p className="text-xs text-brand-gray-400 dark:text-brand-gray-500 font-mono uppercase">
              Query: <span className="text-brand-gray-700 dark:text-brand-gray-300 font-semibold">"{query}"</span>
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs text-brand-gray-500 dark:text-brand-gray-400 font-mono">
            <div className="flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-accent-blue-500" />
              <span>{totalResults} matches</span>
            </div>
            <span>&middot;</span>
            <span>Completed in {executionTime}s</span>
          </div>
        </div>
      )}
    </div>
  );
}
