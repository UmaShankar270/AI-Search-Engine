import React from 'react';
import { Sparkles, Check, AlertTriangle, AlertCircle } from 'lucide-react';

export default function AIAnalysisCard({ analysis }) {
  if (!analysis) return null;

  const scoreItems = [
    { label: 'Maintenance Score', value: analysis.scores.maintenance, color: 'bg-emerald-500' },
    { label: 'Documentation Score', value: analysis.scores.documentation, color: 'bg-accent-blue-500' },
    { label: 'Community Strength', value: analysis.scores.community, color: 'bg-purple-500' },
    { label: 'Code Quality Score', value: analysis.scores.codeQuality, color: 'bg-teal-500' },
    { label: 'Security Compliance', value: analysis.scores.security, color: 'bg-indigo-500' },
  ];

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 shadow-sm text-left space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-3 border-b border-brand-gray-150 dark:border-brand-gray-800/80">
        <h3 className="text-sm font-bold text-brand-gray-955 dark:text-white flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-accent-blue-500 animate-pulse" />
          <span>AI Insight Report</span>
        </h3>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-accent-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/60 text-accent-blue-500 tracking-wide uppercase">
          AI Preview
        </span>
      </div>

      {/* Summary */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Executive Summary
        </h4>
        <p className="text-sm text-brand-gray-600 dark:text-brand-gray-400 leading-relaxed italic">
          "{analysis.summary}"
        </p>
      </div>

      {/* Grid of Scores */}
      <div className="space-y-4">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          AI Score Matrix
        </h4>
        <div className="space-y-3">
          {scoreItems.map((score, idx) => (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-brand-gray-600 dark:text-brand-gray-400">
                <span>{score.label}</span>
                <span className="font-mono text-brand-gray-900 dark:text-white">{score.value}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-brand-gray-100 dark:bg-brand-gray-800 overflow-hidden">
                <div
                  className={`h-full ${score.color} transition-all duration-500`}
                  style={{ width: `${score.value}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-brand-gray-150 dark:border-brand-gray-800/80 pt-4">
        {/* Strengths */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-emerald-600 dark:text-emerald-450 uppercase tracking-wider block font-mono">
            Key Strengths
          </h4>
          <ul className="space-y-2 text-xs text-brand-gray-600 dark:text-brand-gray-450 font-medium">
            {analysis.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <Check className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-red-500 dark:text-red-400 uppercase tracking-wider block font-mono">
            Potential Risks
          </h4>
          <ul className="space-y-2 text-xs text-brand-gray-600 dark:text-brand-gray-450 font-medium">
            {analysis.weaknesses.map((weak, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                <span>{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Best Use Cases */}
      <div className="border-t border-brand-gray-150 dark:border-brand-gray-800/80 pt-4 space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Ideal Deployment Use Cases
        </h4>
        <ul className="list-disc list-inside text-xs text-brand-gray-600 dark:text-brand-gray-405 leading-relaxed space-y-1">
          {analysis.bestUseCases.map((use, idx) => (
            <li key={idx}>{use}</li>
          ))}
        </ul>
      </div>

      {/* Notice */}
      <div className="p-3.5 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-150 dark:border-brand-gray-850 rounded-xl text-center space-y-1 text-xs text-brand-gray-400">
        <AlertTriangle className="w-4 h-4 text-yellow-500 mx-auto" />
        <p className="font-semibold text-brand-gray-700 dark:text-brand-gray-300">FastAPI Ingestion Stub</p>
        <p className="text-[10px] text-brand-gray-400">
          Real-time AI metrics will populate here upon backend REST routing updates.
        </p>
      </div>
    </div>
  );
}
