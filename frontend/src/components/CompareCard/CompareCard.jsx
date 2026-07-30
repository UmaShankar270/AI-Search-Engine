import React from 'react';
import ComparisonHeader from './ComparisonHeader';
import ComparisonTable from './ComparisonTable';
import ComparisonSummary from './ComparisonSummary';
import ComparisonActions from './ComparisonActions';

export default function CompareCard({
  repoA,
  repoB,
  summary,
  onSwap,
  onClear,
}) {
  if (!repoA || !repoB) return null;

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header Info Grid */}
      <ComparisonHeader repoA={repoA} repoB={repoB} />

      {/* Numerical Metrics Side-by-Side Table */}
      <ComparisonTable repoA={repoA} repoB={repoB} />

      {/* AI Comparison Summary Card */}
      <ComparisonSummary
        summary={summary}
        repoAName={repoA.name}
        repoBName={repoB.name}
      />

      {/* Swap / Clear / Link Actions */}
      <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm">
        <ComparisonActions
          repoA={repoA}
          repoB={repoB}
          onSwap={onSwap}
          onClear={onClear}
        />
      </div>
    </div>
  );
}
