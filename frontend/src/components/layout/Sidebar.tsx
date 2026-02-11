import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, LogOut, FileSearch } from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../../contexts/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload', label: 'Upload', icon: Upload },
];

const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 w-60 bg-sidebar-bg flex flex-col z-40">
      {/* Logo */}
      <NavLink to="/dashboard" className="flex items-center gap-2.5 px-5 h-16 border-b border-sidebar-border">
        <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
          <FileSearch className="h-4.5 w-4.5 text-white" />
        </div>
        <span className="text-lg font-bold text-white tracking-tight">Sortex</span>
      </NavLink>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-hover text-sidebar-active'
                  : 'text-sidebar-text hover:bg-sidebar-hover hover:text-sidebar-active'
              )
            }
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="px-3 pb-4 border-t border-sidebar-border pt-4">
        <div className="px-3 mb-3">
          <p className="text-xs font-medium text-sidebar-text truncate">{user?.email}</p>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-sidebar-text hover:bg-sidebar-hover hover:text-sidebar-active transition-colors"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
