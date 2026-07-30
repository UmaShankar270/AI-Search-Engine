import React from 'react';
import { Search, Inbox, AlertOctagon, RefreshCw } from 'lucide-react';

export default function EmptyState({ type = 'empty', title, message, onRetry }) {
  // Config map based on type
  const configs = {
    empty: {
      icon: <Search className="w-12 h-12 text-brand-gray-400 dark:text-brand-gray-600" />,
      title: title || 'Describe your idea or tech stack',
      message: message || 'Type a concept like "fast React state manager" or "Firebase backend database alternative" above to begin AI semantic discovery.'
    },
    'no-results': {
      icon: <Inbox className="w-12 h-12 text-brand-gray-400 dark:text-brand-gray-600" />,
      title: title || 'No repositories found',
      message: message || 'We could not find any matches matching your filters or search query. Try adjusting your constraints or re-evaluating the prompt.'
    },
    error: {
      icon: <AlertOctagon className="w-12 h-12 text-red-500 dark:text-red-400" />,
      title: title || 'An error occurred during discovery',
      message: message || 'Failed to fetch repositories. Check your connection or retry the operation below.'
    }
  };

  const current = configs[type] || configs.empty;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl text-center max-w-lg mx-auto shadow-sm">
      <div className="p-4 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-100 dark:border-brand-gray-800 rounded-2xl mb-4">
        {current.icon}
      </div>
      <h3 className="text-lg font-bold text-brand-gray-950 dark:text-white mb-2">
        {current.title}
      </h3>
      <p className="text-sm text-brand-gray-500 dark:text-brand-gray-400 leading-relaxed mb-6">
        {current.message}
      </p>

      {type === 'error' && onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center space-x-2 px-4 py-2 border border-brand-gray-200 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 text-xs font-semibold text-brand-gray-700 dark:text-brand-gray-300 rounded-lg hover:bg-brand-gray-100 dark:hover:bg-brand-gray-900 transition-colors shadow-sm cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Discovery</span>
        </button>
      )}
    </div>
  );
}
