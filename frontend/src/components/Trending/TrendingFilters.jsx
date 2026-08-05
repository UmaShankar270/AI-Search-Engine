import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, SlidersHorizontal, Search, Flame, Star, GitFork, Calendar } from 'lucide-react';

export default function TrendingFilters({
  searchQuery,
  setSearchQuery,
  filters,
  setFilters,
  isOpen,
  onClose,
  languages = ['All', 'TypeScript', 'JavaScript', 'Python', 'Go', 'Rust'],
}) {
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleReset = () => {
    setSearchQuery('');
    setFilters({
      timeRange: 'today',
      language: 'All',
      sortBy: 'trendingScore',
    });
  };

  const filterContent = (
    <div className="space-y-6 text-left">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-brand-gray-100 dark:border-brand-gray-800 pb-4">
        <h3 className="text-sm font-bold text-brand-gray-955 dark:text-white flex items-center space-x-2">
          <SlidersHorizontal className="w-4 h-4 text-red-500" />
          <span>Trending Filters</span>
        </h3>
        <button
          onClick={handleReset}
          className="text-xs font-semibold text-red-500 hover:underline cursor-pointer"
        >
          Reset all
        </button>
      </div>

      {/* Search Input */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Search Trending
        </label>
        <div className="relative flex items-center border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-xl focus-within:border-red-500 focus-within:ring-1 focus-within:ring-red-500 transition-all text-xs">
          <span className="pl-3 text-brand-gray-405">
            <Search className="w-3.5 h-3.5" />
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by keyword..."
            className="w-full py-2.5 px-2 bg-transparent outline-none border-none text-brand-gray-900 dark:text-white placeholder-brand-gray-450"
          />
        </div>
      </div>

      {/* Time Range */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Time Range
        </label>
        <div className="grid grid-cols-3 gap-1.5 text-xs font-medium">
          {[
            { label: 'Today', value: 'today' },
            { label: 'Week', value: 'week' },
            { label: 'Month', value: 'month' },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleFilterChange('timeRange', opt.value)}
              className={`py-2 rounded-lg border text-center transition-colors cursor-pointer ${
                filters.timeRange === opt.value
                  ? 'bg-brand-gray-955 dark:bg-white text-white dark:text-black border-brand-gray-955 dark:border-white shadow-sm font-semibold'
                  : 'bg-white dark:bg-brand-gray-900 border-brand-gray-200 dark:border-brand-gray-800 text-brand-gray-650 dark:text-brand-gray-350 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="space-y-2.5">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Language
        </label>
        <div className="flex flex-wrap gap-1.5">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => handleFilterChange('language', lang)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                filters.language === lang
                  ? 'bg-brand-gray-955 dark:bg-white text-white dark:text-black border-brand-gray-955 dark:border-white shadow-sm'
                  : 'bg-white dark:bg-brand-gray-900 border-brand-gray-200 dark:border-brand-gray-800 text-brand-gray-650 dark:text-brand-gray-350 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      {/* Sort By */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Sort By
        </label>
        <select
          value={filters.sortBy}
          onChange={(e) => handleFilterChange('sortBy', e.target.value)}
          className="w-full text-sm px-3 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 rounded-xl text-brand-gray-850 dark:text-brand-gray-250 focus:outline-none focus:border-red-500 cursor-pointer"
        >
          <option value="trendingScore">Trending Score (AI-based)</option>
          <option value="stars">Stars (Total)</option>
          <option value="forks">Forks (Total)</option>
          <option value="updated">Recently Updated</option>
        </select>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:block w-64 flex-shrink-0 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm h-fit sticky top-24">
        {filterContent}
      </div>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 lg:hidden flex justify-end">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.4 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="fixed inset-0 bg-black"
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 220 }}
              className="relative w-80 max-w-full bg-white dark:bg-brand-gray-955 h-full p-6 shadow-2xl flex flex-col overflow-y-auto border-l border-brand-gray-200 dark:border-brand-gray-800"
            >
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-lg text-brand-gray-500 hover:text-brand-gray-950 dark:hover:text-white transition-colors cursor-pointer"
                aria-label="Close filters"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="pt-8">{filterContent}</div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
