import React from 'react';
import { GitCompare, Search, Plus } from 'lucide-react';
import CompareSearch from './CompareSearch';

export default function EmptyComparison({
  repoA,
  repoB,
  onSelectRepo,
  onRemoveRepo,
}) {
  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-8 text-center space-y-8 w-full max-w-4xl mx-auto shadow-sm">
      <div className="max-w-md mx-auto space-y-2">
        <div className="w-12 h-12 bg-accent-blue-50 dark:bg-blue-955/30 border border-blue-100 dark:border-blue-900/50 rounded-2xl flex items-center justify-center mx-auto text-accent-blue-500 mb-2">
          <GitCompare className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-brand-gray-955 dark:text-white">
          Side-by-Side Comparison
        </h2>
        <p className="text-sm text-brand-gray-500 dark:text-brand-gray-400">
          Select any two repositories from our discovery index to evaluate code quality, stats, and AI recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
        {/* Repository Slot A */}
        <div className="border border-dashed border-brand-gray-200 dark:border-brand-gray-800 rounded-2xl p-6 flex flex-col justify-center items-center bg-brand-gray-50/50 dark:bg-brand-gray-950/20 min-h-48">
          {repoA ? (
            <div className="space-y-4 w-full text-left">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/60 text-accent-blue-500">
                  SLOT A
                </span>
                <button
                  onClick={() => onRemoveRepo('A')}
                  className="text-xs text-red-500 hover:underline cursor-pointer"
                >
                  Remove
                </button>
              </div>
              <div className="flex items-center space-x-3">
                <img
                  src={repoA.avatar}
                  alt={`${repoA.owner} avatar`}
                  className="w-10 h-10 rounded-lg object-cover border border-brand-gray-150"
                />
                <div>
                  <h4 className="text-sm font-bold text-brand-gray-955 dark:text-white">
                    {repoA.owner}/{repoA.name}
                  </h4>
                  <p className="text-xs text-brand-gray-400 dark:text-brand-gray-500 font-mono">
                    {repoA.language} &bull; {repoA.stars?.toLocaleString()} stars
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 w-full">
              <span className="text-xs font-semibold text-brand-gray-400">Select Repository A</span>
              <CompareSearch label="Search Repo A..." onSelect={(repo) => onSelectRepo('A', repo)} />
            </div>
          )}
        </div>

        {/* Repository Slot B */}
        <div className="border border-dashed border-brand-gray-200 dark:border-brand-gray-800 rounded-2xl p-6 flex flex-col justify-center items-center bg-brand-gray-50/50 dark:bg-brand-gray-950/20 min-h-48">
          {repoB ? (
            <div className="space-y-4 w-full text-left">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-955/20 border border-purple-100 dark:border-purple-900/50 text-purple-500">
                  SLOT B
                </span>
                <button
                  onClick={() => onRemoveRepo('B')}
                  className="text-xs text-red-500 hover:underline cursor-pointer"
                >
                  Remove
                </button>
              </div>
              <div className="flex items-center space-x-3">
                <img
                  src={repoB.avatar}
                  alt={`${repoB.owner} avatar`}
                  className="w-10 h-10 rounded-lg object-cover border border-brand-gray-150"
                />
                <div>
                  <h4 className="text-sm font-bold text-brand-gray-955 dark:text-white">
                    {repoB.owner}/{repoB.name}
                  </h4>
                  <p className="text-xs text-brand-gray-400 dark:text-brand-gray-500 font-mono">
                    {repoB.language} &bull; {repoB.stars?.toLocaleString()} stars
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 w-full">
              <span className="text-xs font-semibold text-brand-gray-400">Select Repository B</span>
              <CompareSearch label="Search Repo B..." onSelect={(repo) => onSelectRepo('B', repo)} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
