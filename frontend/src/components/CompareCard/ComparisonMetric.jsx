import React from 'react';
import { Trophy } from 'lucide-react';

export default function ComparisonMetric({
  label,
  valA,
  valB,
  type = 'number', // 'number', 'string', 'date'
  smallerIsBetter = false,
}) {
  const isNumber = type === 'number';

  let isABetter = false;
  let isBBetter = false;
  let hasDiff = false;

  if (isNumber) {
    const numA = typeof valA === 'number' ? valA : parseFloat(String(valA).replace(/[^0-9.-]/g, '')) || 0;
    const numB = typeof valB === 'number' ? valB : parseFloat(String(valB).replace(/[^0-9.-]/g, '')) || 0;

    if (numA !== numB) {
      hasDiff = true;
      if (smallerIsBetter) {
        isABetter = numA < numB;
        isBBetter = numB < numA;
      } else {
        isABetter = numA > numB;
        isBBetter = numB > numA;
      }
    }
  } else if (type === 'date') {
    const dateA = new Date(valA);
    const dateB = new Date(valB);
    if (!isNaN(dateA) && !isNaN(dateB)) {
      hasDiff = true;
      // Closer/more recent is better
      isABetter = dateA > dateB;
      isBBetter = dateB > dateA;
    }
  }

  const formatDisplay = (val) => {
    if (typeof val === 'number') {
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <div className="grid grid-cols-3 py-3.5 border-b border-brand-gray-100 dark:border-brand-gray-850/60 items-center text-xs font-mono">
      {/* Repo A Value */}
      <div className="text-left pr-4">
        <span
          className={`px-2.5 py-1.5 rounded-lg border font-semibold inline-flex items-center space-x-1 ${
            isABetter
              ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-450 border-emerald-100 dark:border-emerald-900/40'
              : 'bg-transparent text-brand-gray-700 dark:text-brand-gray-300 border-transparent'
          }`}
        >
          <span>{formatDisplay(valA)}</span>
          {isABetter && <Trophy className="w-3.5 h-3.5 text-emerald-500 fill-current ml-1 flex-shrink-0" />}
        </span>
      </div>

      {/* Metric Label */}
      <div className="text-center font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider font-sans text-[10px]">
        {label}
      </div>

      {/* Repo B Value */}
      <div className="text-right pl-4">
        <span
          className={`px-2.5 py-1.5 rounded-lg border font-semibold inline-flex items-center space-x-1 ${
            isBBetter
              ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-450 border-emerald-100 dark:border-emerald-900/40'
              : 'bg-transparent text-brand-gray-700 dark:text-brand-gray-300 border-transparent'
          }`}
        >
          {isBBetter && <Trophy className="w-3.5 h-3.5 text-emerald-500 fill-current mr-1 flex-shrink-0" />}
          <span>{formatDisplay(valB)}</span>
        </span>
      </div>
    </div>
  );
}
