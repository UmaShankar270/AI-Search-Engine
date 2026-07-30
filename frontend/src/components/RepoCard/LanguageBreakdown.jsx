import React from 'react';

export default function LanguageBreakdown({ languages = [] }) {
  if (languages.length === 0) return null;

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm space-y-4 text-left">
      <h3 className="text-xs font-bold text-brand-gray-950 dark:text-white uppercase tracking-wider font-mono">
        Languages Breakdown
      </h3>

      {/* Stacked Progress Bar */}
      <div className="h-2.5 w-full rounded-full bg-brand-gray-100 dark:bg-brand-gray-850 overflow-hidden flex">
        {languages.map((lang, idx) => (
          <div
            key={idx}
            className="h-full transition-all duration-300"
            style={{
              width: `${lang.percentage}%`,
              backgroundColor: lang.color || '#8b949e',
            }}
            title={`${lang.name}: ${lang.percentage}%`}
          />
        ))}
      </div>

      {/* Languages Indicators list */}
      <div className="flex flex-wrap gap-4 pt-1">
        {languages.map((lang, idx) => (
          <div key={idx} className="flex items-center space-x-2 text-xs">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block flex-shrink-0"
              style={{ backgroundColor: lang.color || '#8b949e' }}
            />
            <span className="font-semibold text-brand-gray-800 dark:text-brand-gray-300">
              {lang.name}
            </span>
            <span className="text-brand-gray-400 dark:text-brand-gray-500 font-mono">
              {lang.percentage.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
