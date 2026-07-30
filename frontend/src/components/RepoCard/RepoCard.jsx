import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Star, GitFork, Calendar, ExternalLink, GitCompare, Minus, CheckCircle2 } from 'lucide-react';
import { useApp } from '../../context/AppContext';

const LANGUAGE_COLORS = {
  javascript: '#f1e05a',
  typescript: '#3178c6',
  python: '#3572a5',
  go: '#00add8',
  rust: '#dea584',
  html: '#e34c26',
  css: '#563d7c',
  java: '#b07219',
};

export default function RepoCard({ repo }) {
  const { compareRepos, addRepoToCompare, removeRepoFromCompare } = useApp();

  const isComparing = compareRepos.some((r) => r.id === repo.id);
  const compareCount = compareRepos.length;

  const handleCompareClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isComparing) {
      removeRepoFromCompare(repo.id);
    } else {
      addRepoToCompare(repo);
    }
  };

  const langColor = LANGUAGE_COLORS[repo.language?.toLowerCase()] || '#8b949e';

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getScoreStyle = (score) => {
    if (score >= 90) return 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50';
    if (score >= 75) return 'bg-accent-blue-50 dark:bg-blue-950/20 text-accent-blue-500 dark:text-accent-blue-400 border-blue-200 dark:border-blue-900/50';
    return 'bg-brand-gray-50 dark:bg-brand-gray-900 text-brand-gray-500 dark:text-brand-gray-400 border-brand-gray-200 dark:border-brand-gray-800';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, transition: { duration: 0.15 } }}
      className="group relative flex flex-col justify-between border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-6 shadow-sm hover:border-brand-gray-300 dark:hover:border-brand-gray-700 hover:shadow-md transition-all duration-200 text-left"
    >
      <div>
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-center space-x-3 truncate">
            <img
              src={repo.avatar || 'https://images.unsplash.com/photo-1618401471353-b98aedd07871?auto=format&fit=crop&w=80&h=80&q=80'}
              alt={`${repo.owner} avatar`}
              className="w-8 h-8 rounded-lg object-cover border border-brand-gray-100 dark:border-brand-gray-800 flex-shrink-0"
              loading="lazy"
            />
            <Link
              to={`/repo/${repo.owner}/${repo.name}`}
              className="text-base font-bold text-brand-gray-955 dark:text-white hover:text-accent-blue-500 transition-colors truncate"
            >
              <span className="text-brand-gray-400 dark:text-brand-gray-500 font-normal">{repo.owner}/</span>
              {repo.name}
            </Link>
          </div>

          {repo.matchScore && (
            <div className={`flex items-center px-2.5 py-0.5 rounded-full border text-xs font-bold whitespace-nowrap ${getScoreStyle(repo.matchScore)}`}>
              <span>{repo.matchScore}% Match</span>
            </div>
          )}
        </div>

        <p className="text-sm text-brand-gray-500 dark:text-brand-gray-400 mb-4 line-clamp-2 leading-relaxed">
          {repo.description}
        </p>

        {repo.matchReasonBullets && repo.matchReasonBullets.length > 0 && (
          <div className="p-4 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-100 dark:border-brand-gray-850 rounded-xl mb-4">
            <span className="text-[10px] font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block mb-2 font-mono">
              Why this repository matches
            </span>
            <ul className="space-y-1.5 text-xs text-brand-gray-600 dark:text-brand-gray-400 font-medium">
              {repo.matchReasonBullets.map((bullet, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-450 mt-0.5 flex-shrink-0" />
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {repo.topics && repo.topics.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4 justify-start">
            {repo.topics.map((topic) => (
              <span
                key={topic}
                className="text-[10px] px-2 py-0.5 rounded bg-brand-gray-100 dark:bg-brand-gray-950 border border-brand-gray-200/50 dark:border-brand-gray-800/60 text-brand-gray-600 dark:text-brand-gray-400 font-medium font-mono"
              >
                #{topic}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-4 pt-4 border-t border-brand-gray-100 dark:border-brand-gray-800/60">
        <div className="flex items-center justify-between text-xs text-brand-gray-500 dark:text-brand-gray-400 font-mono">
          <div className="flex items-center space-x-4">
            {repo.language && (
              <div className="flex items-center space-x-1.5">
                <span
                  className="w-2.5 h-2.5 rounded-full inline-block"
                  style={{ backgroundColor: langColor }}
                />
                <span className="text-brand-gray-700 dark:text-brand-gray-300 font-semibold font-sans">{repo.language}</span>
              </div>
            )}
            <div className="flex items-center space-x-1">
              <Star className="w-3.5 h-3.5 fill-current text-yellow-500" />
              <span>{repo.stars?.toLocaleString() || 0}</span>
            </div>
            <div className="flex items-center space-x-1">
              <GitFork className="w-3.5 h-3.5" />
              <span>{repo.forks?.toLocaleString() || 0}</span>
            </div>
          </div>

          <div className="flex items-center space-x-1 text-[10px] text-brand-gray-400 dark:text-brand-gray-500">
            <span>Updated {formatDate(repo.lastUpdated)}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 pt-1.5 w-full justify-between items-center">
          <div className="flex items-center space-x-1.5">
            <Link
              to={`/repo/${repo.owner}/${repo.name}`}
              className="px-3 py-1.5 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 text-xs font-semibold bg-white dark:bg-brand-gray-900 text-brand-gray-700 dark:text-brand-gray-305 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850 hover:text-brand-gray-955 dark:hover:text-white transition-colors cursor-pointer shadow-sm"
            >
              View Details
            </Link>

            <a
              href={`https://github.com/${repo.owner}/${repo.name}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 text-xs text-brand-gray-405 hover:text-brand-gray-950 dark:hover:text-white transition-colors"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <button
            onClick={handleCompareClick}
            disabled={!isComparing && compareCount >= 2}
            className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-colors cursor-pointer ${
              isComparing
                ? 'text-red-600 dark:text-red-400 border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-955/20 hover:bg-red-100 dark:hover:bg-red-955/40'
                : compareCount >= 2
                ? 'text-brand-gray-300 dark:text-brand-gray-750 border-brand-gray-150 dark:border-brand-gray-900 cursor-not-allowed'
                : 'text-brand-gray-750 dark:text-brand-gray-300 border-brand-gray-200 dark:border-brand-gray-800 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-850'
            }`}
          >
            {isComparing ? (
              <>
                <Minus className="w-3.5 h-3.5" />
                <span>Remove Compare</span>
              </>
            ) : (
              <>
                <GitCompare className="w-3.5 h-3.5" />
                <span>Compare</span>
              </>
            )}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
