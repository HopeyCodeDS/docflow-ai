import React from 'react';
import clsx from 'clsx';

interface SkeletonProps {
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({ className }) => (
  <div className={clsx('animate-pulse rounded bg-slate-200', className)} />
);

const SkeletonTableRow: React.FC<{ columns: number }> = ({ columns }) => (
  <tr>
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="px-4 py-3">
        <Skeleton className="h-4 w-full" />
      </td>
    ))}
  </tr>
);

const SkeletonCard: React.FC = () => (
  <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
    <Skeleton className="w-12 h-12 rounded-lg" />
    <div className="flex-1">
      <Skeleton className="h-3 w-20 mb-2" />
      <Skeleton className="h-6 w-12" />
    </div>
  </div>
);

export { Skeleton, SkeletonTableRow, SkeletonCard };
