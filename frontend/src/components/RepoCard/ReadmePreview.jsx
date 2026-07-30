import React from 'react';
import { BookOpen, FileCode } from 'lucide-react';

export default function ReadmePreview({ readmeHtml = '' }) {
  // Simple custom mock parser to render markdown syntax on-the-fly for visual preview
  const parseMarkdown = (markdownText) => {
    if (!markdownText) return '';
    
    return markdownText
      .split('\n')
      .map((line, idx) => {
        // Heading 1
        if (line.startsWith('# ')) {
          return (
            <h1 key={idx} className="text-2xl font-extrabold border-b border-brand-gray-100 dark:border-brand-gray-800 pb-2 mb-4 text-brand-gray-950 dark:text-white mt-4 first:mt-0 text-left">
              {line.replace('# ', '')}
            </h1>
          );
        }
        // Heading 3
        if (line.startsWith('### ')) {
          return (
            <h3 key={idx} className="text-base font-bold text-brand-gray-950 dark:text-white mt-4 mb-2 text-left">
              {line.replace('### ', '')}
            </h3>
          );
        }
        // Code Block
        if (line.startsWith('```')) {
          if (line.length > 3) {
            // Start code block
            return null; // Handle inside block grouping
          }
          return null;
        }
        // Code line simulation
        if (line.includes('npm install') || line.includes('const ') || line.includes('function ') || line.includes('import ')) {
          return (
            <pre key={idx} className="bg-brand-gray-50 dark:bg-brand-gray-950 p-3 rounded-lg font-mono text-xs border border-brand-gray-200/50 dark:border-brand-gray-850 overflow-x-auto text-left text-brand-gray-800 dark:text-brand-gray-300 my-2">
              {line}
            </pre>
          );
        }
        // Blank line
        if (!line.trim()) {
          return <div key={idx} className="h-2" />;
        }
        // List item
        if (line.startsWith('- ')) {
          return (
            <ul key={idx} className="list-disc list-inside text-sm text-brand-gray-600 dark:text-brand-gray-400 text-left pl-2 space-y-1">
              <li>{line.replace('- ', '')}</li>
            </ul>
          );
        }
        // Standard Paragraph
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
      <div className="px-5 py-4 border-b border-brand-gray-100 dark:border-brand-gray-800 bg-brand-gray-50 dark:bg-brand-gray-950 flex items-center space-x-2">
        <BookOpen className="w-4 h-4 text-brand-gray-400" />
        <span className="text-xs font-bold text-brand-gray-600 dark:text-brand-gray-405 uppercase tracking-wider font-mono">
          README.md
        </span>
      </div>

      {/* Scrollable container */}
      <div className="p-6 max-h-96 overflow-y-auto space-y-2 scrollbar-thin">
        {parseMarkdown(readmeHtml)}
      </div>
    </div>
  );
}
