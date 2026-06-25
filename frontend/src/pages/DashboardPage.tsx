import { useState, useEffect } from 'react';
import { FileText, Clock, AlertTriangle, Filter, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { UploadDropzone } from '../components/upload/UploadDropzone';
import { UploadProgressModal } from '../components/upload/UploadProgressModal';

const mockContracts = [
  { id: '1', filename: 'Master_Service_Agrmt_2024_v2.pdf', type: 'MSA', score: 82, scoreLevel: 'HIGH', status: 'Completed', date: '2024-10-12' },
  { id: '2', filename: 'Global_NDA_Vendor_Network.docx', type: 'NDA', score: 12, scoreLevel: 'LOW', status: 'Completed', date: '2024-10-14' },
  { id: '3', filename: 'Lease_Agreement_DC_Office.pdf', type: 'LEASE', score: null, scoreLevel: 'CALC', status: 'Analyzing', date: '2024-10-15' },
];

type StageStatus = 'pending' | 'active' | 'complete';

export function DashboardPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadFilename, setUploadFilename] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  const defaultStages = [
    { id: 'extract', label: 'EXTRACTING TEXT', status: 'pending' as StageStatus },
    { id: 'segment', label: 'SEGMENTING CLAUSES', status: 'pending' as StageStatus },
    { id: 'assess', label: 'ASSESSING RISK', status: 'pending' as StageStatus },
    { id: 'benchmark', label: 'BENCHMARKING', status: 'pending' as StageStatus },
  ];
  
  const [stages, setStages] = useState(defaultStages);

  useEffect(() => {
    if (!isUploading) return;

    let progressInterval: number;
    
    // Simulate progression of stages
    if (currentStageIndex < stages.length) {
      setStages(prev => prev.map((s, i) => {
        if (i < currentStageIndex) return { ...s, status: 'complete' };
        if (i === currentStageIndex) return { ...s, status: 'active', progress: uploadProgress };
        return { ...s, status: 'pending' };
      }));

      progressInterval = window.setInterval(() => {
        setUploadProgress(p => {
          if (p >= 100) {
            setCurrentStageIndex(idx => idx + 1);
            return 0;
          }
          return p + Math.floor(Math.random() * 15) + 5;
        });
      }, 500);
    } else {
      // Finished all stages
      setStages(prev => prev.map(s => ({ ...s, status: 'complete' })));
      setTimeout(() => {
        setIsUploading(false);
        // Could navigate to detail page here
      }, 1000);
    }

    return () => window.clearInterval(progressInterval);
  }, [isUploading, currentStageIndex, uploadProgress, stages.length]);

  const handleFileUpload = (file: File) => {
    setUploadFilename(file.name);
    setStages(defaultStages);
    setCurrentStageIndex(0);
    setUploadProgress(0);
    setIsUploading(true);
  };


  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 relative">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-xs font-semibold text-slate-400 tracking-wider">TOTAL CONTRACTS</h3>
            <div className="w-8 h-8 rounded bg-brand-800 flex items-center justify-center text-accent">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-5xl font-serif text-slate-100 mb-2">1,279</div>
            <div className="text-xs text-slate-400">
              <span className="text-slate-200 font-medium">+12.5%</span> vs last month
            </div>
          </div>
        </div>

        <div className="card p-6 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-xs font-semibold text-slate-400 tracking-wider">PENDING ANALYSIS</h3>
            <div className="w-8 h-8 rounded bg-brand-800 flex items-center justify-center text-slate-300">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-5xl font-serif text-slate-100 mb-4">17</div>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-1.5 bg-brand-800 rounded-full overflow-hidden">
                <div className="h-full bg-accent w-3/4"></div>
              </div>
              <span className="text-xs text-slate-400 font-mono">75%</span>
            </div>
          </div>
        </div>

        <div className="card p-6 flex flex-col justify-between border-l-4 border-l-danger">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-xs font-semibold text-danger tracking-wider">HIGH RISK ALERTS</h3>
            <div className="w-8 h-8 rounded bg-danger-subtle flex items-center justify-center text-danger">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-5xl font-serif text-slate-100 mb-4">02</div>
            <button className="text-sm text-danger hover:text-danger/80 transition-colors flex items-center gap-1 group">
              Review Critical Findings 
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </button>
          </div>
        </div>
      </div>

      {/* Upload Dropzone */}
      <UploadDropzone onFileAccepted={handleFileUpload} />

      {/* Header & Actions */}
      <div className="flex justify-between items-end pt-4">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-serif font-medium text-slate-100 mb-2">Contract Portfolio</h2>
          <p className="text-slate-400 text-sm">Advanced management and risk assessment of institutional legal assets powered by neural clause extraction.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <Filter className="w-4 h-4" /> Filter
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-brand-960 text-slate-400 text-xs tracking-wider border-b border-brand-800/50">
            <tr>
              <th className="px-6 py-4 font-medium uppercase">Filename</th>
              <th className="px-6 py-4 font-medium uppercase">Type</th>
              <th className="px-6 py-4 font-medium uppercase">Risk Score</th>
              <th className="px-6 py-4 font-medium uppercase">Status</th>
              <th className="px-6 py-4 font-medium uppercase">Upload Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-800/50">
            {mockContracts.map((contract) => (
              <tr key={contract.id} className="hover:bg-brand-960/50 transition-colors group cursor-pointer">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="text-accent bg-brand-800 p-1.5 rounded">
                      <FileText className="w-4 h-4" />
                    </div>
                    <span className="font-medium text-slate-200 group-hover:text-accent transition-colors">
                      {contract.filename}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-[10px] font-semibold tracking-wider text-slate-300 bg-brand-800 rounded border border-brand-700 uppercase">
                    {contract.type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col gap-1 items-start">
                    <span className="font-mono text-lg text-slate-200">
                      {contract.score ?? '--'}
                    </span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wider ${
                      contract.scoreLevel === 'HIGH' ? 'bg-danger-subtle text-danger border border-danger/20' :
                      contract.scoreLevel === 'LOW' ? 'bg-success-subtle text-success border border-success/20' :
                      'bg-brand-800 text-slate-400 border border-brand-700'
                    }`}>
                      {contract.scoreLevel === 'CALC' ? 'CALCULATING' : `${contract.scoreLevel} RISK`}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-slate-300">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      contract.status === 'Completed' ? 'bg-slate-300' : 'bg-accent animate-pulse'
                    }`}></span>
                    {contract.status}
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-400 font-mono text-xs">
                  {contract.date}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Pagination Footer */}
        <div className="px-6 py-4 border-t border-brand-800/50 flex justify-between items-center bg-brand-960/30">
          <span className="text-xs text-slate-400 tracking-wide uppercase">Showing 3 of 1,284 documents</span>
          <div className="flex gap-2">
            <button className="p-1 rounded bg-brand-800 text-slate-400 hover:text-slate-200 hover:bg-brand-700 transition-colors">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="p-1 rounded bg-brand-800 text-slate-400 hover:text-slate-200 hover:bg-brand-700 transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {isUploading && (
        <UploadProgressModal 
          filename={uploadFilename} 
          stages={stages} 
          onCancel={() => setIsUploading(false)} 
        />
      )}
    </div>
  );
}
