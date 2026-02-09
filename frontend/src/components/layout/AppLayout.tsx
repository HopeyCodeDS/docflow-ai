import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const AppLayout: React.FC = () => (
  <div className="min-h-screen bg-slate-50">
    <Sidebar />
    <main className="ml-60 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <Outlet />
      </div>
    </main>
  </div>
);

export default AppLayout;
