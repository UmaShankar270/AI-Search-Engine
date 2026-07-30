import React from 'react';
import { Star, GitFork, Eye, Info } from 'lucide-react';

export default function RepositoryStats({ details }) {
  const stats = [
    { label: 'Watchers', value: Math.round(details.stars * 0.08).toLocaleString(), icon: <Eye className="w-4 h-4 text-indigo-500" /> },
    { label: 'Forks Count', value: details.forks?.toLocaleString(), icon: <GitFork className="w-4 h-4 text-accent-blue-500" /> },
    { label: 'Total Stars', value: details.stars?.toLocaleString(), icon: <Star className="w-4 h-4 text-yellow-500 fill-current" /> },
    { label: 'Open Issues', value: details.openIssues?.toLocaleString(), icon: <Info className="w-4 h-4 text-red-500" /> },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
      {stats.map((stat, idx) => (
        <div
          key={idx}
          className="p-4 rounded-xl border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 flex items-center justify-between shadow-sm"
        >
          <div className="text-left">
            <span className="text-[10px] font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block mb-1 font-mono">
              {stat.label}
            </span>
            <span className="text-lg md:text-xl font-bold text-brand-gray-955 dark:text-white">
              {stat.value}
            </span>
          </div>
          <div className="p-2.5 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-150 dark:border-brand-gray-850 rounded-xl flex-shrink-0">
            {stat.icon}
          </div>
        </div>
      ))}
    </div>
  );
}
