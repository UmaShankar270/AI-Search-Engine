import React, { useRef, useEffect } from 'react';
import { Search, Command } from 'lucide-react';

export default function SearchBar({ value, onChange, onSubmit }) {
  const inputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Focus on Cmd/Ctrl + K or "/"
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      } else if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <form onSubmit={onSubmit} className="relative w-full group">
      <div className="absolute inset-0 bg-gradient-to-r from-accent-blue-500/20 via-indigo-500/20 to-purple-500/20 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      
      <div className="relative flex items-center w-full border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl focus-within:border-accent-blue-500 focus-within:ring-2 focus-within:ring-accent-blue-500/15 focus-within:shadow-lg transition-all duration-200 shadow-sm">
        <div className="pl-4 text-brand-gray-400 dark:text-brand-gray-650 flex-shrink-0">
          <Search className="w-5 h-5" />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Describe target codebase stack (e.g. 'high speed react state toolsMIT' or '/') ..."
          className="w-full text-sm md:text-base px-3.5 py-4 bg-transparent border-none outline-none text-brand-gray-950 dark:text-white placeholder-brand-gray-400 focus:ring-0 focus:outline-none"
        />

        <div className="hidden sm:flex items-center space-x-1.5 pr-4 flex-shrink-0 text-brand-gray-400 dark:text-brand-gray-600 font-mono text-[10px] select-none pointer-events-none">
          <kbd className="px-1.5 py-0.5 rounded border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950">
            <Command className="w-2.5 h-2.5 inline" />
          </kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 rounded border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950">
            K
          </kbd>
        </div>
      </div>
    </form>
  );
}
