import React from 'react';
import { Activity, GitCommit, GitPullRequest, Milestone, HelpCircle } from 'lucide-react';

export default function RepositoryActivity({ activity }) {
  if (!activity) return null;

  const activities = [
    { label: 'Commit Frequency', value: activity.commitRate, desc: 'Average weekly commits count', icon: <GitCommit className="w-4 h-4 text-emerald-500" /> },
    { label: 'Issue Close Ratio', value: activity.issueCloseRate, desc: 'Percent of total issues closed', icon: <HelpCircle className="w-4 h-4 text-red-500" /> },
    { label: 'PR Merge Frequency', value: activity.prMergeRate, desc: 'Weekly pull requests merged', icon: <GitPullRequest className="w-4 h-4 text-purple-500" /> },
    { label: 'Release Frequency', value: activity.releaseFrequency, desc: 'Version tag update cycles', icon: <Milestone className="w-4 h-4 text-accent-blue-500" /> },
  ];

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm text-left space-y-4">
      <h3 className="text-xs font-bold text-brand-gray-950 dark:text-white uppercase tracking-wider font-mono flex items-center space-x-1.5">
        <Activity className="w-4 h-4 text-brand-gray-400" />
        <span>Repository Activity Indicators</span>
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
        {activities.map((act, idx) => (
          <div key={idx} className="p-3 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-150 dark:border-brand-gray-850 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {act.icon}
                <span className="text-xs font-bold text-brand-gray-800 dark:text-brand-gray-300">
                  {act.label}
                </span>
              </div>
              <span className="text-xs font-bold font-mono text-brand-gray-900 dark:text-white">
                {act.value}%
              </span>
            </div>
            
            {/* Progress indicators bar */}
            <div className="h-1.5 w-full bg-brand-gray-200 dark:bg-brand-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${act.value}%` }}
              />
            </div>
            <p className="text-[10px] text-brand-gray-450 leading-normal">
              {act.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
