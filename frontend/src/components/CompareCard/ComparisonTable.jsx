import React from 'react';
import ComparisonMetric from './ComparisonMetric';
import TechStackBadges from '../RepoCard/TechStackBadges';

export default function ComparisonTable({ repoA, repoB }) {
  if (!repoA || !repoB) return null;

  // Derive extra details
  const watchersA = Math.round(repoA.stars * 0.08);
  const watchersB = Math.round(repoB.stars * 0.08);

  const prsA = Math.round(repoA.forks * 0.15);
  const prsB = Math.round(repoB.forks * 0.15);

  const sizeA = repoA.size || '4.8 MB';
  const sizeB = repoB.size || '24.1 MB';

  const defaultBranchA = repoA.defaultBranch || 'main';
  const defaultBranchB = repoB.defaultBranch || 'main';

  const releaseA = repoA.latestRelease || 'v4.5.2';
  const releaseB = repoB.latestRelease || 'v2.45.1';

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm text-center space-y-4">
      <h3 className="text-xs font-bold text-brand-gray-955 dark:text-white uppercase tracking-wider font-mono text-left pb-3 border-b border-brand-gray-100 dark:border-brand-gray-850">
        Metric Breakdown
      </h3>

      <div className="space-y-1">
        {/* Stars */}
        <ComparisonMetric label="Stars" valA={repoA.stars} valB={repoB.stars} />

        {/* Forks */}
        <ComparisonMetric label="Forks" valA={repoA.forks} valB={repoB.forks} />

        {/* Watchers */}
        <ComparisonMetric label="Watchers" valA={watchersA} valB={watchersB} />

        {/* Open Issues */}
        <ComparisonMetric label="Open Issues" valA={repoA.openIssues} valB={repoB.openIssues} smallerIsBetter />

        {/* Pull Requests */}
        <ComparisonMetric label="Pull Requests" valA={prsA} valB={prsB} />

        {/* License */}
        <ComparisonMetric label="License" valA={repoA.license} valB={repoB.license} type="string" />

        {/* Language */}
        <ComparisonMetric label="Language" valA={repoA.language} valB={repoB.language} type="string" />

        {/* Repository Size */}
        <ComparisonMetric label="Repo Size" valA={sizeA} valB={sizeB} type="string" />

        {/* Default Branch */}
        <ComparisonMetric label="Default Branch" valA={defaultBranchA} valB={defaultBranchB} type="string" />

        {/* Latest Release */}
        <ComparisonMetric label="Latest Release" valA={releaseA} valB={releaseB} type="string" />

        {/* Last Updated */}
        <ComparisonMetric label="Last Updated" valA={repoA.lastUpdated} valB={repoB.lastUpdated} type="date" />

        {/* Commit Activity */}
        <ComparisonMetric
          label="Commit Activity"
          valA={repoA.activity?.commitRate || 80}
          valB={repoB.activity?.commitRate || 85}
        />
      </div>

      {/* Side-by-Side Topics display */}
      <div className="grid grid-cols-2 gap-6 pt-4 border-t border-brand-gray-100 dark:border-brand-gray-850">
        {/* Repo A Topics */}
        <div className="text-left space-y-2">
          <span className="text-[10px] font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
            Slot A Topics
          </span>
          <TechStackBadges topics={repoA.topics} />
        </div>

        {/* Repo B Topics */}
        <div className="text-right space-y-2">
          <span className="text-[10px] font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
            Slot B Topics
          </span>
          <div className="flex flex-wrap gap-1.5 justify-end">
            {repoB.topics.map((t) => (
              <span
                key={t}
                className="text-xs px-2.5 py-1 rounded-md bg-brand-gray-50 dark:bg-brand-gray-955 border border-brand-gray-200 dark:border-brand-gray-805 text-brand-gray-750 dark:text-brand-gray-400 font-medium"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
