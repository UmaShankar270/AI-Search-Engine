import React from 'react';
import { BookOpen, FolderOpen, Globe, Tag, Check } from 'lucide-react';
import TechStackBadges from './TechStackBadges';

export default function RepositoryOverview({ details }) {
  const metaItems = [
    { label: 'Size', value: details.size || 'N/A' },
    { label: 'Created Date', value: details.createdDate || 'N/A' },
    { label: 'Latest Release', value: details.latestRelease || 'None' },
    { label: 'Default Branch', value: details.defaultBranch || 'main' },
    { label: 'Visibility', value: details.visibility || 'Public' },
  ];

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 shadow-sm text-left space-y-6">
      {/* About Section */}
      <div className="space-y-2">
        <h3 className="text-sm font-bold text-brand-gray-950 dark:text-white flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-brand-gray-400" />
          <span>About</span>
        </h3>
        <p className="text-sm text-brand-gray-600 dark:text-brand-gray-400 leading-relaxed">
          {details.about || details.description}
        </p>
      </div>

      {/* Homepage Link */}
      {details.homepageUrl && (
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
            Website
          </h4>
          <a
            href={details.homepageUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-accent-blue-500 hover:underline inline-flex items-center space-x-1 font-semibold"
          >
            <Globe className="w-4 h-4 mr-1 inline" />
            <span>{details.homepageUrl}</span>
          </a>
        </div>
      )}

      {/* Tech stack topics */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono flex items-center">
          <Tag className="w-3.5 h-3.5 mr-1" />
          <span>Topics</span>
        </h4>
        <TechStackBadges topics={details.topics} />
      </div>

      {/* Grid of properties metadata */}
      <div className="border-t border-brand-gray-150 dark:border-brand-gray-800/80 pt-4 space-y-3">
        <h4 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block font-mono">
          Specifications
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-xs font-mono text-brand-gray-600 dark:text-brand-gray-400">
          {metaItems.map((item, idx) => (
            <div key={idx} className="flex justify-between py-1.5 border-b border-brand-gray-100 dark:border-brand-gray-850/50 last:border-0">
              <span className="text-brand-gray-450">{item.label}</span>
              <span className="font-semibold text-brand-gray-900 dark:text-white">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
