import React from 'react';
import clsx from 'clsx';
import { getConfidenceClass } from '../../constants';

interface ConfidenceBarProps {
  confidence: number;
}

const colorMap = {
  high: { badge: 'bg-emerald-50 text-emerald-700', bar: 'bg-emerald-500' },
  medium: { badge: 'bg-amber-50 text-amber-700', bar: 'bg-amber-500' },
  low: { badge: 'bg-red-50 text-red-700', bar: 'bg-red-500' },
};

const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ confidence }) => {
  const level = getConfidenceClass(confidence);
  const colors = colorMap[level];
  const pct = Math.round(confidence * 100);

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-300', colors.bar)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span
        className={clsx(
          'text-xs font-semibold px-2 py-0.5 rounded-full',
          colors.badge
        )}
      >
        {pct}%
      </span>
    </div>
  );
};

export default ConfidenceBar;
