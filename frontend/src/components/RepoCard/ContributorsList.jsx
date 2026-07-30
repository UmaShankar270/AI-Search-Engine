import React from 'react';
import { Users } from 'lucide-react';

export default function ContributorsList({ contributors = [] }) {
  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm text-left space-y-4">
      <h3 className="text-xs font-bold text-brand-gray-955 dark:text-white uppercase tracking-wider font-mono flex items-center space-x-1.5">
        <Users className="w-4 h-4 text-brand-gray-400" />
        <span>Top Contributors</span>
      </h3>

      <div className="space-y-3">
        {contributors.map((contrib, idx) => (
          <div key={idx} className="flex items-center justify-between py-1.5 border-b border-brand-gray-100 dark:border-brand-gray-850/50 last:border-0 last:pb-0">
            <div className="flex items-center space-x-3">
              <img
                src={contrib.avatar}
                alt={`${contrib.username} avatar`}
                className="w-7 h-7 rounded-full object-cover border border-brand-gray-100 dark:border-brand-gray-800 flex-shrink-0"
              />
              <span className="text-xs font-bold text-brand-gray-800 dark:text-brand-gray-250 hover:text-accent-blue-500 cursor-pointer transition-colors">
                {contrib.username}
              </span>
            </div>
            <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-200/50 dark:border-brand-gray-800 text-brand-gray-550 dark:text-brand-gray-400">
              {contrib.contributions} commits
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
