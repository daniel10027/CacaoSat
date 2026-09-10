import { cn } from '@/lib/cn';

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn('font-display font-extrabold tracking-tight', className)}>
      <span className="text-ci-orange">CACAO</span>
      <span className="text-ci-green">SAT</span>
    </span>
  );
}

export function FlagRibbon({ className }: { className?: string }) {
  return (
    <span
      className={cn('block h-1 w-full rounded-full', className)}
      style={{
        background: 'linear-gradient(90deg,#FF7A00 0 33%,#FFFFFF 33% 66%,#00A651 66% 100%)',
      }}
    />
  );
}
