import { cn } from '@/lib/cn';

export function Spinner({ label, className }: { label?: string; className?: string }) {
  return (
    <div className={cn('flex items-center gap-3 text-sm text-sand/70', className)} role="status">
      <span className="relative inline-block h-5 w-5">
        <span className="absolute inset-0 rounded-full border-2 border-white/15" />
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-ci-orange" />
      </span>
      {label}
    </div>
  );
}
