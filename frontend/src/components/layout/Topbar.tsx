import { Bell, HelpCircle } from 'lucide-react';

export function Topbar() {
  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-brand-800/50 bg-brand-950">
      <div className="flex-1">
        <div className="relative w-96">
          <input 
            type="text" 
            placeholder="Search legal repository..." 
            className="w-full bg-brand-960 border border-brand-800 rounded-md py-2 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 transition-colors"
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4 text-slate-400">
          <button className="hover:text-slate-200 transition-colors relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-accent rounded-full border border-brand-950"></span>
          </button>
          <button className="hover:text-slate-200 transition-colors">
            <HelpCircle className="w-5 h-5" />
          </button>
        </div>
        
        <button className="flex items-center gap-2 text-accent font-semibold text-sm hover:text-accent-hover transition-colors">
          NEW UPLOAD
        </button>
      </div>
    </header>
  );
}
