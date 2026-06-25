import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileType } from 'lucide-react';
import { cn } from '../../lib/utils';

interface UploadDropzoneProps {
  onFileAccepted: (file: File) => void;
}

export function UploadDropzone({ onFileAccepted }: UploadDropzoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileAccepted(acceptedFiles[0]);
    }
  }, [onFileAccepted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  return (
    <div 
      {...getRootProps()} 
      className={cn(
        "border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200",
        isDragActive 
          ? "border-accent bg-accent/5" 
          : "border-brand-800 hover:border-brand-600 hover:bg-brand-960/50"
      )}
    >
      <input {...getInputProps()} />
      <div className={cn(
        "w-12 h-12 rounded-full flex items-center justify-center mb-4 transition-colors",
        isDragActive ? "bg-accent/20 text-accent" : "bg-brand-900 text-slate-400"
      )}>
        <UploadCloud className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-medium text-slate-200 mb-2">
        {isDragActive ? "Drop contract here" : "Securely drop document"}
      </h3>
      <p className="text-sm text-slate-400 max-w-sm mb-6">
        Upload a single PDF or docx file. Our SOC2 Type II compliant pipeline encrypts your data at rest and in transit.
      </p>
      <div className="flex gap-4 text-xs font-medium text-slate-500 uppercase tracking-wider">
        <span className="flex items-center gap-1"><FileType className="w-3.5 h-3.5" /> PDF</span>
        <span className="flex items-center gap-1"><FileType className="w-3.5 h-3.5" /> DOCX</span>
      </div>
    </div>
  );
}
