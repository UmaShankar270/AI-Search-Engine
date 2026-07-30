import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Compass, GitCompare } from 'lucide-react';
import SearchBar from '../components/SearchBar/SearchBar';
import { useApp } from '../context/AppContext';

export default function Home() {
  const [query, setQuery] = useState('');
  const { setSearchQuery } = useApp();
  const navigate = useNavigate();

  const handleSearchSubmit = (e) => {
    if (!query.trim()) return;
    setSearchQuery(query);
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  const handleExampleClick = (exampleText) => {
    setQuery(exampleText);
    setSearchQuery(exampleText);
    navigate(`/search?q=${encodeURIComponent(exampleText)}`);
  };

  const searchExamples = [
    'Fast state management for React with zero-boilerplate',
    'Self-hosted alternative to Firebase database',
    'Modern charting library in React using SVG',
    'Tailwind-based components library with high accessibility',
  ];

  const features = [
    {
      icon: <Sparkles className="w-5 h-5 text-accent-blue-500" />,
      title: 'AI Semantic Search',
      description: 'Search GitHub repos by describing your ideas or requirements in natural language.',
    },
    {
      icon: <GitCompare className="w-5 h-5 text-purple-500" />,
      title: 'Repo Comparison',
      description: 'Select any two repositories to compare stars, open issues, and code health side-by-side.',
    },
    {
      icon: <Compass className="w-5 h-5 text-emerald-500" />,
      title: 'Explore Trending',
      description: 'Stay updated with curated open-source projects popular across developer communities.',
    },
  ];

  return (
    <div className="flex-1 flex flex-col justify-center items-center py-16 px-4 md:py-24">
      <div className="text-center max-w-3xl mx-auto space-y-6 mb-12">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-xs font-medium text-brand-gray-600 dark:text-brand-gray-400 shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-accent-blue-500" />
          <span>Semantic Repository Search Engine</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-4xl sm:text-6xl font-extrabold tracking-tight text-brand-gray-955 dark:text-white leading-tight"
        >
          Discover repositories
          <br />
          <span className="bg-gradient-to-r from-accent-blue-500 via-indigo-500 to-purple-500 bg-clip-text text-transparent">
            semantically.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-base sm:text-lg text-brand-gray-500 dark:text-brand-gray-400 max-w-2xl mx-auto leading-relaxed"
        >
          Search GitHub by concepts, use cases, and descriptions rather than just keywords. Combine with Linear & Vercel speeds to compare side-by-side.
        </motion.p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="w-full max-w-2xl px-2 mb-6"
      >
        <SearchBar value={query} onChange={setQuery} onSubmit={handleSearchSubmit} />
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="w-full max-w-2xl px-2 mb-16 text-center"
      >
        <p className="text-xs text-brand-gray-450 dark:text-brand-gray-500 mb-2 font-medium">
          Try semantic queries:
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {searchExamples.map((example) => (
            <button
              key={example}
              onClick={() => handleExampleClick(example)}
              className="text-xs px-3 py-1.5 rounded-full border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-650 dark:text-brand-gray-400 hover:border-brand-gray-300 dark:hover:border-brand-gray-700 hover:text-brand-gray-950 dark:hover:text-white transition-colors cursor-pointer"
            >
              "{example}"
            </button>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="w-full max-w-5xl px-4 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in"
      >
        {features.map((feature, i) => (
          <div
            key={i}
            className="p-6 rounded-2xl border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 shadow-sm hover:shadow transition-all duration-200 flex flex-col items-start text-left"
          >
            <div className="p-2.5 rounded-lg bg-brand-gray-50 dark:bg-brand-gray-950 mb-4 border border-brand-gray-100 dark:border-brand-gray-800">
              {feature.icon}
            </div>
            <h3 className="text-base font-semibold text-brand-gray-955 dark:text-white mb-2">
              {feature.title}
            </h3>
            <p className="text-sm text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed">
              {feature.description}
            </p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
