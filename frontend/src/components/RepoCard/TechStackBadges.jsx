import React from 'react';

export default function TechStackBadges({ topics = [] }) {
  if (topics.length === 0) return <p className="text-xs text-brand-gray-400">No topics defined.</p>;

  return (
    <div className="flex flex-wrap gap-1.5 justify-start">
      {topics.map((topic) => (
        <span
          key={topic}
          className="text-xs px-2.5 py-1 rounded-md bg-brand-gray-50 dark:bg-brand-gray-955 border border-brand-gray-200 dark:border-brand-gray-805 text-brand-gray-700 dark:text-brand-gray-400 font-medium"
        >
          {topic}
        </span>
      ))}
    </div>
  );
}
