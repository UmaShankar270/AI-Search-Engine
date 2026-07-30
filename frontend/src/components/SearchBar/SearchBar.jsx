import React, { useRef, useEffect } from 'react';
import { Search, Sparkles, Command } from 'lucide-react';

export default function SearchBar({ value, onChange, onSubmit, placeholder = 'Search repositories using AI semantic query...' }) {
  const inputRef = useRef(null);

  // Keyboard shortcut listener to focus search bar
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Focus on '/' or 'Ctrl+K' / 'Cmd+K'
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative group">
        {/* Glow backdrop on focus */}
        <div className="absolute -inset-0.5 bg-gradient-to-r from-accent-blue-500 to-indigo-500 rounded-xl blur opacity-10 group-focus-within:opacity-25 transition duration-200" />
        
        <div className="relative flex items-center bg-white dark:bg-brand-gray-900 border border-brand-gray-200 dark:border-brand-gray-800 rounded-xl shadow-sm overflow-hidden group-focus-within:border-accent-blue-500 transition-colors">
          {/* AI Sparkle Icon */}
          <div className="flex items-center pl-4 text-brand-gray-400 dark:text-brand-gray-500">
            <Sparkles className="w-5 h-5 text-accent-blue-500 animate-pulse" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="w-full py-4 pl-3 pr-20 text-sm md:text-base bg-transparent border-0 text-brand-gray-950 dark:text-white placeholder-brand-gray-400 dark:placeholder-brand-gray-500 focus:outline-none focus:ring-0"
            id="ai-search-input"
          />

          {/* Action elements inside search bar */}
          <div className="absolute right-3 flex items-center space-x-2">
            {/* Keyboard shortcut hint */}
            <div className="hidden sm:flex items-center space-x-1 px-1.5 py-1 rounded border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 text-[10px] text-brand-gray-400 font-mono">
              <Command className="w-2.5 h-2.5" />
              <span>K</span>
            </div>

            <button
              type="submit"
              className="p-2 rounded-lg bg-brand-gray-950 dark:bg-white text-white dark:text-black hover:bg-brand-gray-800 dark:hover:bg-brand-gray-100 transition-colors cursor-pointer shadow"
              aria-label="Search button"
            >
              <Search className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}
