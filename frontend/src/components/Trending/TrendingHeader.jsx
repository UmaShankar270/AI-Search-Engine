import React from 'react';
import { Flame, Activity } from 'lucide-react';

export default function TrendingHeader({ totalCount, timeRange }) {
  const rangeLabels = {
    today: 'today',
    week: 'this week',
    month: 'this month',
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-brand-gray-150 dark:border-brand-gray-800 pb-4 gap-4 text-left">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-brand-gray-955 dark:text-white flex items-center space-x-2">
          <Flame className="w-5 h-5 text-red-500 fill-current animate-pulse" />
          <span>Trending Repositories</span>
        </h2>
        <p className="text-xs text-brand-gray-400 dark:text-brand-gray-550 font-mono uppercase">
          Ecosystem Heatmap & Developer Velocity Matrix
        </p>
      </div>

      <div className="flex items-center space-x-2 text-xs font-mono text-brand-gray-500 dark:text-brand-gray-400">
        <Activity className="w-4 h-4 text-red-500" />
        <span>{totalCount} repositories hot {rangeLabels[timeRange] || 'today'}</span>
      </div>
    </div>
  );
}
