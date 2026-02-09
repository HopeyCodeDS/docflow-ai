import React from 'react';
import clsx from 'clsx';

interface StatsCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  iconBg?: string;
  iconColor?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({
  label,
  value,
  icon,
  iconBg = 'bg-brand-50',
  iconColor = 'text-brand-600',
}) => (
  <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex items-center gap-4">
    <div
      className={clsx(
        'flex-shrink-0 flex items-center justify-center w-12 h-12 rounded-lg',
        iconBg,
        iconColor
      )}
    >
      {icon}
    </div>
    <div>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  </div>
);

export default StatsCard;
