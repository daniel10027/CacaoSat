import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { api } from '@/lib/api';
import type { Paginated, Alert } from '@/types/api';

export function AlertBell() {
  const { data } = useQuery({
    queryKey: ['alerts', 'unack-count'],
    queryFn: () =>
      api<Paginated<Alert>>('/alerts?acknowledged=false&per_page=1'),
    refetchInterval: 20_000,
  });
  const count = data?.pagination.total ?? 0;

  return (
    <Link
      to="/app/alertes"
      className="relative rounded-lg p-2 text-sand/70 transition-colors hover:bg-white/5 hover:text-white"
      aria-label={`${count} alertes non acquittées`}
    >
      <Bell size={18} />
      {count > 0 && (
        <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-risk-high px-1 text-[10px] font-bold text-white">
          {count > 99 ? '99+' : count}
        </span>
      )}
    </Link>
  );
}
