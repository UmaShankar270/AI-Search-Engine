import React from 'react';
import { Flame, Star, Award, TrendingUp } from 'lucide-react';

export default function TrendingStats({ stats }) {
  if (!stats) return null;

  const statItems = [
    {
      label: 'Trending Projects',
      value: stats.totalTrending,
      desc: 'Active repositories cataloged',
      icon: <Flame className="w-5 h-5 text-red-500" />,
    },
    {
      label: 'Dominant Language',
      value: stats.mostPopularLanguage,
      desc: 'Highest language density today',
      icon: <Award className="w-5 h-5 text-indigo-500" />,
    },
    {
      label: 'Leaderboard Growth',
      value: stats.highestGrowthRepo?.name || 'N/A',
      desc: stats.highestGrowthRepo?.growth || '',
      icon: <TrendingUp className="w-5 h-5 text-emerald-500" />,
      isRepo: true,
      owner: stats.highestGrowthRepo?.owner
    },
    {
      label: 'Mean Stars Velocity',
      value: `+${stats.averageStarsGained}`,
      desc: 'Average daily stars increase',
      icon: <Star className="w-5 h-5 text-yellow-500 fill-current" />,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
      {statItems.map((item, idx) => (
        <div
          key={idx}
          className="p-5 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl flex flex-col justify-between shadow-sm text-left space-y-2 relative overflow-hidden"
        >
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
              {item.label}
            </span>
            <div className="p-1.5 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-150 dark:border-brand-gray-850 rounded-lg flex-shrink-0">
              {item.icon}
            </div>
          </div>
          <div className="space-y-1">
            <h4 className="text-base sm:text-lg font-bold text-brand-gray-955 dark:text-white truncate tracking-tight">
              {item.isRepo && item.owner ? (
                <>
                  <span className="text-brand-gray-400 font-normal text-sm">{item.owner}/</span>
                  {item.value}
                </>
              ) : (
                item.value
              )}
            </h4>
            <p className="text-[10px] text-brand-gray-450 dark:text-brand-gray-500 leading-normal leading-relaxed truncate">
              {item.desc}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
