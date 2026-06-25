import { Check, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Stage {
  id: string;
  label: string;
  status: 'complete' | 'active' | 'pending';
  progress?: number; // 0-100 for active stage
}

interface UploadProgressModalProps {
  filename: string;
  stages: Stage[];
  onCancel: () => void;
}

export function UploadProgressModal({ filename, stages, onCancel }: UploadProgressModalProps) {
  return (
    <div className="fixed inset-0 bg-brand-950/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="w-[500px] card border-brand-800 p-10 relative shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="font-serif text-2xl text-slate-100 mb-2">
            Analyzing<br />
            <span className="text-slate-300">'{filename}'...</span>
          </h2>
          <p className="text-sm text-slate-400 font-serif italic">
            AI engine performing multi-stage risk cross-referencing
          </p>
        </div>

        <div className="space-y-4 mb-10">
          {stages.map((stage, index) => {
            const isComplete = stage.status === 'complete';
            const isActive = stage.status === 'active';
            const isPending = stage.status === 'pending';

            return (
              <div 
                key={stage.id}
                className={cn(
                  "border rounded p-4 flex items-center gap-4 transition-all duration-300",
                  isComplete ? "bg-brand-960 border-brand-800 text-slate-300" :
                  isActive ? "bg-brand-960 border-accent/50 text-accent shadow-[0_0_15px_rgba(242,201,96,0.05)]" :
                  "bg-brand-950 border-brand-900 text-slate-600"
                )}
              >
                <div className={cn(
                  "w-6 h-6 rounded flex items-center justify-center shrink-0",
                  isComplete ? "bg-brand-800 text-slate-300" :
                  isActive ? "bg-accent/20 text-accent" :
                  "bg-brand-900 text-slate-600"
                )}>
                  {isComplete && <Check className="w-3.5 h-3.5" />}
                  {isActive && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {isPending && <span className="text-xs font-mono">{index + 1}</span>}
                </div>
                
                <div className="flex-1 flex items-center justify-between">
                  <span className="text-xs tracking-widest font-medium uppercase">
                    {stage.label}
                  </span>
                  
                  {isActive && stage.progress !== undefined && (
                    <div className="w-24 h-1.5 bg-brand-900 rounded-full overflow-hidden ml-4">
                      <div 
                        className="h-full bg-gradient-to-r from-accent to-accent/50 transition-all duration-500"
                        style={{ width: `${stage.progress}%` }}
                      />
                    </div>
                  )}

                  {!isActive && (
                    <span className={cn(
                      "text-[10px] uppercase tracking-wider font-semibold",
                      isComplete ? "text-slate-500" : "text-slate-700"
                    )}>
                      {stage.status}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-center">
          <button 
            onClick={onCancel}
            className="text-xs tracking-widest uppercase font-semibold text-slate-400 hover:text-slate-200 transition-colors"
          >
            Cancel Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
