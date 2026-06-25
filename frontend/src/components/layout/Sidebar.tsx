import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FolderOpen, Settings, Scale } from 'lucide-react';
import { cn } from '../../lib/utils';

export function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Portfolio', path: '/portfolio', icon: FolderOpen },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-brand-960 h-screen flex flex-col border-r border-brand-800/50 flex-shrink-0">
      {/* Logo Area */}
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-accent rounded flex items-center justify-center">
          <Scale className="w-5 h-5 text-brand-950" />
        </div>
        <div>
          <h1 className="text-accent font-serif font-semibold text-lg leading-tight">ClauseIQ</h1>
          <p className="text-[10px] text-slate-400 tracking-widest uppercase">Legal Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-medium transition-colors",
                isActive 
                  ? "bg-brand-900 text-accent border-l-2 border-accent" 
                  : "text-slate-300 hover:bg-brand-900/50 hover:text-slate-100 border-l-2 border-transparent"
              )
            }
          >
            <item.icon className="w-4 h-4" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-brand-800/50">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-10 h-10 rounded-full bg-brand-800 border border-brand-700 overflow-hidden">
            <img src="https://i.pravatar.cc/150?u=a042581f4e29026704d" alt="Julian Thorne" className="w-full h-full object-cover" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-200">Julian Thorne</p>
            <p className="text-xs text-slate-400">Senior Counsel</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
