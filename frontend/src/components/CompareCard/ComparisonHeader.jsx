import React from 'react';
import { ExternalLink, HelpCircle } from 'lucide-react';

export default function ComparisonHeader({ repoA, repoB }) {
  if (!repoA || !repoB) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-stretch text-left">
      {/* Repo A header info */}
      <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 flex flex-col justify-between shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-accent-blue-500" />
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center space-x-3.5 truncate">
              <img
                src={repoA.avatar}
                alt={`${repoA.owner} avatar`}
                className="w-11 h-11 rounded-xl object-cover border border-brand-gray-150 flex-shrink-0"
              />
              <div className="truncate">
                <span className="text-[10px] font-bold font-mono text-accent-blue-500 tracking-wider uppercase block">
                  Repository A
                </span>
                <h3 className="text-lg md:text-xl font-extrabold text-brand-gray-955 dark:text-white truncate tracking-tight">
                  <span className="text-brand-gray-400 font-normal">{repoA.owner}/</span>
                  {repoA.name}
                </h3>
              </div>
            </div>

            <a
              href={`https://github.com/${repoA.owner}/${repoA.name}`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 transition-colors text-brand-gray-405 hover:text-brand-gray-900 dark:hover:text-white"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          <p className="text-xs text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed line-clamp-2">
            {repoA.description}
          </p>
        </div>
      </div>

      {/* Repo B header info */}
      <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 flex flex-col justify-between shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-purple-500" />
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center space-x-3.5 truncate">
              <img
                src={repoB.avatar}
                alt={`${repoB.owner} avatar`}
                className="w-11 h-11 rounded-xl object-cover border border-brand-gray-150 flex-shrink-0"
              />
              <div className="truncate">
                <span className="text-[10px] font-bold font-mono text-purple-500 tracking-wider uppercase block">
                  Repository B
                </span>
                <h3 className="text-lg md:text-xl font-extrabold text-brand-gray-955 dark:text-white truncate tracking-tight">
                  <span className="text-brand-gray-400 font-normal">{repoB.owner}/</span>
                  {repoB.name}
                </h3>
              </div>
            </div>

            <a
              href={`https://github.com/${repoB.owner}/${repoB.name}`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 transition-colors text-brand-gray-405 hover:text-brand-gray-900 dark:hover:text-white"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          <p className="text-xs text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed line-clamp-2">
            {repoB.description}
          </p>
        </div>
      </div>
    </div>
  );
}
