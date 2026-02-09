import React from 'react';
import clsx from 'clsx';

const variants = {
  success: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  warning: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  danger: 'bg-red-50 text-red-700 ring-red-600/20',
  info: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  secondary: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  brand: 'bg-brand-50 text-brand-700 ring-brand-600/20',
};

interface BadgeProps {
  variant?: keyof typeof variants;
  children: React.ReactNode;
  className?: string;
  dot?: boolean;
}

const Badge: React.FC<BadgeProps> = ({ variant = 'secondary', children, className, dot }) => (
  <span
    className={clsx(
      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset',
      variants[variant],
      className
    )}
  >
    {dot && (
      <span
        className={clsx('h-1.5 w-1.5 rounded-full', {
          'bg-emerald-500': variant === 'success',
          'bg-amber-500': variant === 'warning',
          'bg-red-500': variant === 'danger',
          'bg-blue-500': variant === 'info',
          'bg-slate-400': variant === 'secondary',
          'bg-brand-500': variant === 'brand',
        })}
      />
    )}
    {children}
  </span>
);

export default Badge;
