import React, { useState, useRef, useEffect } from 'react';
import { Search } from 'lucide-react';
import { mockRepositories } from '../../data/mockRepositories';

export default function CompareSearch({ label, onSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showOptions, setShowOptions] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const filtered = mockRepositories.filter((repo) => {
      const matchText = `${repo.owner}/${repo.name} ${repo.language}`.toLowerCase();
      return matchText.includes(query.toLowerCase());
    });
    setResults(filtered);
  }, [query]);

  // Click outside to dismiss options dropdown
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowOptions(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleSelectOption = (repo) => {
    onSelect(repo);
    setQuery('');
    setResults([]);
    setShowOptions(false);
  };

  return (
    <div ref={containerRef} className="relative w-full text-left">
      <div className="relative flex items-center border border-brand-gray-250 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-xl focus-within:border-accent-blue-500 focus-within:ring-1 focus-within:ring-accent-blue-500 transition-all text-xs">
        <span className="pl-3 text-brand-gray-400">
          <Search className="w-3.5 h-3.5" />
        </span>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowOptions(true);
          }}
          onFocus={() => setShowOptions(true)}
          placeholder={label}
          className="w-full py-2.5 px-2 bg-transparent outline-none border-none text-brand-gray-900 dark:text-white placeholder-brand-gray-450"
        />
      </div>

      {showOptions && query.trim() && (
        <div className="absolute z-10 w-full mt-1 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-xl shadow-lg max-h-52 overflow-y-auto">
          {results.length === 0 ? (
            <div className="p-3 text-xs text-brand-gray-450 text-center">
              No matching repositories in index
            </div>
          ) : (
            results.map((repo) => (
              <button
                key={repo.id}
                onClick={() => handleSelectOption(repo)}
                className="w-full text-left p-3 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 flex items-center space-x-2 border-b border-brand-gray-100 dark:border-brand-gray-850 last:border-0 cursor-pointer"
              >
                <img
                  src={repo.avatar}
                  alt={`${repo.owner} avatar`}
                  className="w-6 h-6 rounded-md object-cover flex-shrink-0"
                />
                <div className="truncate">
                  <div className="text-xs font-bold text-brand-gray-850 dark:text-white truncate">
                    {repo.owner}/{repo.name}
                  </div>
                  <div className="text-[10px] text-brand-gray-400 font-mono">
                    {repo.language} &bull; {repo.stars?.toLocaleString()} stars
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
