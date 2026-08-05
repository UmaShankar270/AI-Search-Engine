import React, { useRef, useEffect, useState } from 'react';
import { Search, Command } from 'lucide-react';

export default function SearchBar({ value, onChange, onSubmit }) {
  const inputRef = useRef(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);

  const suggestionsList = [
    'chatbot',
    'video editor',
    'portfolio website',
    'machine learning',
    'spring boot',
    'python automation',
    'react dashboard',
    'AI image generator',
    'Fast state management for React',
    'Self-hosted alternative to Firebase'
  ];

  const filteredSuggestions = suggestionsList.filter(
    (s) =>
      s.toLowerCase().includes((value || '').toLowerCase()) &&
      s.toLowerCase() !== (value || '').toLowerCase()
  );

  // Reset active suggestion index when query value changes
  useEffect(() => {
    setActiveSuggestionIndex(-1);
  }, [value]);

  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      // Focus on Cmd/Ctrl + K or "/"
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      } else if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleInputKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestionIndex((prev) =>
        prev < filteredSuggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestionIndex((prev) =>
        prev > 0 ? prev - 1 : filteredSuggestions.length - 1
      );
    } else if (e.key === 'Enter') {
      if (activeSuggestionIndex >= 0 && activeSuggestionIndex < filteredSuggestions.length) {
        e.preventDefault();
        const selected = filteredSuggestions[activeSuggestionIndex];
        onChange(selected);
        setShowSuggestions(false);
        // Force submit chosen suggestion
        setTimeout(() => {
          const form = inputRef.current?.closest('form');
          if (form) {
            const submitEvent = new Event('submit', { cancelable: true, bubbles: true });
            form.dispatchEvent(submitEvent);
          }
        }, 50);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

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
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyDown={handleInputKeyDown}
          placeholder="Describe target codebase stack (e.g. 'high speed react state tools' or '/') ..."
          className="w-full text-sm md:text-base px-3.5 py-4 bg-transparent border-none outline-none text-brand-gray-955 dark:text-white placeholder-brand-gray-400 focus:ring-0 focus:outline-none"
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

      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-white dark:bg-brand-gray-900 border border-brand-gray-200 dark:border-brand-gray-800 rounded-2xl shadow-xl overflow-hidden text-left max-h-60 overflow-y-auto">
          <ul className="py-2">
            {filteredSuggestions.map((s, idx) => (
              <li key={s}>
                <button
                  type="button"
                  onMouseDown={() => {
                    onChange(s);
                    setTimeout(() => {
                      const form = inputRef.current?.closest('form');
                      if (form) {
                        const submitEvent = new Event('submit', { cancelable: true, bubbles: true });
                        form.dispatchEvent(submitEvent);
                      }
                    }, 50);
                  }}
                  className={`w-full px-4 py-3 text-sm text-brand-gray-700 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 hover:text-brand-gray-955 dark:hover:text-white transition-colors cursor-pointer text-left flex items-center space-x-2.5 ${
                    idx === activeSuggestionIndex ? 'bg-brand-gray-50 dark:bg-brand-gray-850 text-brand-gray-955 dark:text-white' : ''
                  }`}
                >
                  <Search className="w-4 h-4 text-brand-gray-400 dark:text-brand-gray-600" />
                  <span>{s}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}
