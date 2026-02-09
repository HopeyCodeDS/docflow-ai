import React from 'react';
import { Check, Loader2, Circle, XCircle, CircleDot } from 'lucide-react';
import clsx from 'clsx';

interface PipelineStepsProps {
  stages: readonly string[];
  currentStatus: string | null;
}

const ACTIVELY_PROCESSING = new Set(['PROCESSING']);

const PipelineSteps: React.FC<PipelineStepsProps> = ({ stages, currentStatus }) => {
  const currentIndex = currentStatus ? stages.indexOf(currentStatus) : -1;
  const isFailed = currentStatus === 'FAILED';
  const isActivelyProcessing = currentStatus ? ACTIVELY_PROCESSING.has(currentStatus) : false;

  return (
    <div className="flex items-center gap-1 overflow-x-auto py-2">
      {stages.map((stage, i) => {
        const isDone = i < currentIndex && !isFailed;
        const isCurrent = currentStatus === stage;
        const isFailedStep = stage === 'FAILED' && isFailed;
        const isPending = !isDone && !isCurrent;

        return (
          <React.Fragment key={stage}>
            <div
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors',
                isDone && 'bg-emerald-50 text-emerald-700',
                isCurrent && !isFailedStep && (isActivelyProcessing ? 'bg-brand-100 text-brand-700' : 'bg-brand-100 text-brand-700'),
                isFailedStep && 'bg-red-50 text-red-700',
                isPending && 'bg-slate-100 text-slate-400'
              )}
            >
              {isDone && <Check className="h-3.5 w-3.5" />}
              {isCurrent && !isFailedStep && isActivelyProcessing && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              {isCurrent && !isFailedStep && !isActivelyProcessing && <CircleDot className="h-3.5 w-3.5" />}
              {isFailedStep && <XCircle className="h-3.5 w-3.5" />}
              {isPending && <Circle className="h-3 w-3" />}
              {stage.charAt(0) + stage.slice(1).toLowerCase().replace(/_/g, ' ')}
            </div>
            {i < stages.length - 1 && (
              <div
                className={clsx(
                  'w-6 h-0.5 flex-shrink-0',
                  i < currentIndex ? 'bg-emerald-300' : 'bg-slate-200'
                )}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default PipelineSteps;
