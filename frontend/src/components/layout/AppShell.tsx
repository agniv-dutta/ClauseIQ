import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell() {
  return (
    <div className="flex h-screen bg-brand-950 overflow-hidden text-slate-200 font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-auto bg-brand-950 p-6 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
