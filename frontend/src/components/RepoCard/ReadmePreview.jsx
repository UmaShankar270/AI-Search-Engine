import React from 'react';
import { BookOpen } from 'lucide-react';

export default function ReadmePreview({ readmeHtml = '' }) {
  const parseMarkdown = (markdownText) => {
    if (!markdownText) return '';
    
    return markdownText
      .split('\n')
      .map((line, idx) => {
        if (line.startsWith('# ')) {
          return (
            <h1 key={idx} className="text-2xl font-extrabold border-b border-brand-gray-100 dark:border-brand-gray-805 pb-2 mb-4 text-brand-gray-955 dark:text-white mt-4 first:mt-0 text-left">
              {line.replace('# ', '')}
            </h1>
          );
        }
        if (line.startsWith('### ')) {
          return (
            <h3 key={idx} className="text-base font-bold text-brand-gray-955 dark:text-white mt-4 mb-2 text-left">
              {line.replace('### ', '')}
            </h3>
          );
        }
        if (line.startsWith('```')) {
          return null;
        }
        if (line.includes('npm install') || line.includes('const ') || line.includes('function ') || line.includes('import ')) {
          return (
            <pre key={idx} className="bg-brand-gray-50 dark:bg-brand-gray-950 p-3 rounded-lg font-mono text-xs border border-brand-gray-200/50 dark:border-brand-gray-850 overflow-x-auto text-left text-brand-gray-800 dark:text-brand-gray-300 my-2">
              {line}
            </pre>
          );
        }
        if (!line.trim()) {
          return <div key={idx} className="h-2" />;
        }
        if (line.startsWith('- ')) {
          return (
            <ul key={idx} className="list-disc list-inside text-sm text-brand-gray-600 dark:text-brand-gray-400 text-left pl-2 space-y-1">
              <li>{line.replace('- ', '')}</li>
            </ul>
          );
        }
        return (
          <p key={idx} className="text-sm text-brand-gray-600 dark:text-brand-gray-400 leading-relaxed text-left">
            {line}
          </p>
        );
      })
      .filter(Boolean);
  };

  return (
    <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl overflow-hidden shadow-sm flex flex-col text-left">
      <div className="px-5 py-4 border-b border-brand-gray-100 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-955 flex items-center space-x-2">
        <BookOpen className="w-4 h-4 text-brand-gray-400" />
        <span className="text-xs font-bold text-brand-gray-605 dark:text-brand-gray-400 uppercase tracking-wider font-mono">
          README.md
        </span>
      </div>

      <div className="p-6 max-h-96 overflow-y-auto space-y-2 scrollbar-thin">
        {parseMarkdown(readmeHtml)}
      </div>
    </div>
  );
}
