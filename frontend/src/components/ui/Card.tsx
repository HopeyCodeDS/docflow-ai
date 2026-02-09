import React from 'react';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: boolean;
}

const Card: React.FC<CardProps> = ({ children, className, padding = true }) => (
  <div
    className={clsx(
      'bg-white rounded-xl border border-slate-200 shadow-sm',
      padding && 'p-6',
      className
    )}
  >
    {children}
  </div>
);

interface CardHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({ title, description, action }) => (
  <div className="flex items-center justify-between mb-4">
    <div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {description && <p className="text-sm text-slate-500 mt-0.5">{description}</p>}
    </div>
    {action}
  </div>
);

export { Card, CardHeader };
