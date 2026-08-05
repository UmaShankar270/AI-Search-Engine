import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyTrending({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl text-center max-w-lg mx-auto shadow-sm w-full">
      <div className="p-4 bg-brand-gray-50 dark:bg-brand-gray-950 border border-brand-gray-100 dark:border-brand-gray-800 rounded-2xl mb-4">
        <Inbox className="w-12 h-12 text-brand-gray-400 dark:text-brand-gray-650" />
      </div>
      <h3 className="text-lg font-bold text-brand-gray-955 dark:text-white mb-2">
        No Trending Matches
      </h3>
      <p className="text-sm text-brand-gray-500 dark:text-brand-gray-405 leading-relaxed max-w-xs">
        {message || 'We could not find any matching trending repositories. Try clearing your search keyword or selecting a different language.'}
      </p>
    </div>
  );
}
