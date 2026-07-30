import React from 'react';
import { Sparkles, Check, AlertTriangle } from 'lucide-react';

export default function ComparisonSummary({ summary, repoAName, repoBName }) {
  if (!summary) return null;

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 shadow-sm text-left space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-3 border-b border-brand-gray-150 dark:border-brand-gray-800/80">
        <h3 className="text-sm font-bold text-brand-gray-955 dark:text-white flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-accent-blue-500 animate-pulse" />
          <span>AI Comparative Recommendations</span>
        </h3>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-accent-blue-50 dark:bg-blue-955/40 border border-blue-100 dark:border-blue-900/60 text-accent-blue-500 tracking-wide uppercase">
          AI Summary
        </span>
      </div>

      {/* Winner Summary */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Overall Recommended Choice
        </h4>
        <p className="text-sm font-bold text-brand-gray-955 dark:text-white leading-normal">
          🏆 {summary.winner}
        </p>
      </div>

      {/* Strengths lists split */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-brand-gray-100 dark:border-brand-gray-850 pt-4">
        {/* Strengths A */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-accent-blue-500 uppercase tracking-wider block font-mono">
            Strengths of {repoAName}
          </h4>
          <ul className="space-y-2 text-xs text-brand-gray-600 dark:text-brand-gray-450 font-medium">
            {summary.strengthsA.map((str, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <Check className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Strengths B */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-purple-500 uppercase tracking-wider block font-mono">
            Strengths of {repoBName}
          </h4>
          <ul className="space-y-2 text-xs text-brand-gray-600 dark:text-brand-gray-455 font-medium">
            {summary.strengthsB.map((str, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <Check className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommended Use Cases */}
      <div className="border-t border-brand-gray-100 dark:border-brand-gray-850 pt-4 space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Recommended Use Case Scope
        </h4>
        <p className="text-xs text-brand-gray-600 dark:text-brand-gray-405 leading-relaxed">
          {summary.useCases}
        </p>
      </div>

      {/* Migration Difficulty */}
      <div className="border-t border-brand-gray-100 dark:border-brand-gray-850 pt-4 space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Migration & Integration Cost
        </h4>
        <p className="text-xs text-brand-gray-605 dark:text-brand-gray-400 leading-relaxed font-semibold">
          {summary.difficulty}
        </p>
      </div>

      {/* Community Activity */}
      <div className="border-t border-brand-gray-100 dark:border-brand-gray-850 pt-4 space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Ecosystem Activity Comparison
        </h4>
        <p className="text-xs text-brand-gray-605 dark:text-brand-gray-400 leading-relaxed">
          {summary.activity}
        </p>
      </div>

      {/* Notice */}
      <div className="p-3.5 bg-brand-gray-55 dark:bg-brand-gray-955 border border-brand-gray-150 dark:border-brand-gray-850 rounded-xl text-center space-y-1 text-xs text-brand-gray-400">
        <AlertTriangle className="w-4 h-4 text-yellow-500 mx-auto" />
        <p className="font-semibold text-brand-gray-700 dark:text-brand-gray-300">FastAPI Comparison Ingestion Stub</p>
        <p className="text-[10px] text-brand-gray-400">
          Real-time comparative AI recommendations will populate here upon backend REST routing updates.
        </p>
      </div>
    </div>
  );
}
