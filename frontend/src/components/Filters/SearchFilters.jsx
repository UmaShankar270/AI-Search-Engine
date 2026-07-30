import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, SlidersHorizontal, Star, GitFork, Shield, Calendar } from 'lucide-react';

export default function SearchFilters({
  filters,
  setFilters,
  isOpen,
  onClose,
  languages = ['All', 'TypeScript', 'JavaScript', 'Python', 'Go', 'Rust'],
  licenses = ['All', 'MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'],
}) {
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleReset = () => {
    setFilters({
      language: 'All',
      stars: 'All',
      forks: 'All',
      license: 'All',
      updated: 'All',
      sortBy: 'match',
    });
  };

  const filterContent = (
    <div className="space-y-6 text-left">
      <div className="flex items-center justify-between border-b border-brand-gray-100 dark:border-brand-gray-800/60 pb-4">
        <h3 className="text-sm font-bold text-brand-gray-955 dark:text-white flex items-center space-x-2">
          <SlidersHorizontal className="w-4 h-4 text-accent-blue-500" />
          <span>Filters</span>
        </h3>
        <button
          onClick={handleReset}
          className="text-xs font-semibold text-accent-blue-500 hover:underline cursor-pointer"
        >
          Reset all
        </button>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Sort By
        </label>
        <select
          value={filters.sortBy}
          onChange={(e) => handleFilterChange('sortBy', e.target.value)}
          className="w-full text-sm px-3 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 rounded-xl text-brand-gray-850 dark:text-brand-gray-250 focus:outline-none focus:border-accent-blue-500 cursor-pointer"
        >
          <option value="match">Relevance (AI Score)</option>
          <option value="stars">Stars (High to Low)</option>
          <option value="forks">Forks (High to Low)</option>
          <option value="updated">Recently Updated</option>
          <option value="name">Name (Alphabetical)</option>
        </select>
      </div>

      <div className="space-y-2.5">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Language
        </label>
        <div className="flex flex-wrap gap-1.5">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => handleFilterChange('language', lang)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
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

      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono flex items-center">
          <Star className="w-3.5 h-3.5 text-yellow-500 mr-1 fill-current" />
          <span>Stars</span>
        </label>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            { label: 'Any', value: 'All' },
            { label: '> 10k', value: '10000' },
            { label: '> 40k', value: '40000' },
            { label: '> 70k', value: '70000' },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleFilterChange('stars', opt.value)}
              className={`px-3 py-2 rounded-lg border text-center font-medium transition-colors cursor-pointer ${
                filters.stars === opt.value
                  ? 'bg-brand-gray-955 dark:bg-white text-white dark:text-black border-brand-gray-955 dark:border-white shadow-sm'
                  : 'bg-white dark:bg-brand-gray-900 border-brand-gray-200 dark:border-brand-gray-800 text-brand-gray-650 dark:text-brand-gray-350 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-855'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono flex items-center">
          <GitFork className="w-3.5 h-3.5 text-accent-blue-500 mr-1" />
          <span>Forks</span>
        </label>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            { label: 'Any', value: 'All' },
            { label: '> 1k', value: '1000' },
            { label: '> 3k', value: '3000' },
            { label: '> 5k', value: '5000' },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleFilterChange('forks', opt.value)}
              className={`px-3 py-2 rounded-lg border text-center font-medium transition-colors cursor-pointer ${
                filters.forks === opt.value
                  ? 'bg-brand-gray-955 dark:bg-white text-white dark:text-black border-brand-gray-955 dark:border-white shadow-sm'
                  : 'bg-white dark:bg-brand-gray-900 border-brand-gray-200 dark:border-brand-gray-800 text-brand-gray-650 dark:text-brand-gray-350 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-855'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono flex items-center">
          <Shield className="w-3.5 h-3.5 text-indigo-500 mr-1" />
          <span>License</span>
        </label>
        <select
          value={filters.license}
          onChange={(e) => handleFilterChange('license', e.target.value)}
          className="w-full text-sm px-3 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 rounded-xl text-brand-gray-850 dark:text-brand-gray-250 focus:outline-none focus:border-accent-blue-500 cursor-pointer"
        >
          {licenses.map((lic) => (
            <option key={lic} value={lic}>
              {lic === 'All' ? 'Any License' : lic}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono flex items-center">
          <Calendar className="w-3.5 h-3.5 text-emerald-500 mr-1" />
          <span>Recently Updated</span>
        </label>
        <select
          value={filters.updated}
          onChange={(e) => handleFilterChange('updated', e.target.value)}
          className="w-full text-sm px-3 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 rounded-xl text-brand-gray-855 dark:text-brand-gray-255 focus:outline-none focus:border-accent-blue-500 cursor-pointer"
        >
          <option value="All">Any Time</option>
          <option value="3">Last 3 days</option>
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
        </select>
      </div>
    </div>
  );

  return (
    <>
      <div className="hidden lg:block w-64 flex-shrink-0 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm h-fit sticky top-24">
        {filterContent}
      </div>

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
              className="relative w-80 max-w-full bg-white dark:bg-brand-gray-950 h-full p-6 shadow-2xl flex flex-col overflow-y-auto border-l border-brand-gray-200 dark:border-brand-gray-800"
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
