import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DashboardSummary } from '@/types/api';

const AXIS = { stroke: '#5b6b63', fontSize: 11 };
const GRID = 'rgba(255,255,255,0.06)';

const tooltipStyle = {
  contentStyle: {
    background: '#0E211A',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 12,
    fontSize: 12,
    color: '#F4EAD5',
  },
  labelStyle: { color: '#fff' },
} as const;

export function ScoreHistogram({ data }: { data: DashboardSummary['score_distribution'] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
        <XAxis dataKey="range" tickLine={false} axisLine={{ stroke: GRID }} tick={AXIS} />
        <YAxis allowDecimals={false} tickLine={false} axisLine={{ stroke: GRID }} tick={AXIS} />
        <Tooltip {...tooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={i >= 4 ? '#00A651' : i >= 2 ? '#E8A33D' : '#C0392B'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ComplianceTrend({ data }: { data: DashboardSummary['trend'] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
        <defs>
          <linearGradient id="trend" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#00A651" stopOpacity={0.5} />
            <stop offset="1" stopColor="#00A651" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="month" tickLine={false} axisLine={{ stroke: GRID }} tick={AXIS} />
        <YAxis
          domain={[0, 100]}
          tickLine={false}
          axisLine={{ stroke: GRID }}
          tick={AXIS}
          unit="%"
        />
        <Tooltip {...tooltipStyle} formatter={(v: number) => [`${v} %`, 'Conformes']} />
        <Area
          type="monotone"
          dataKey="compliant_pct"
          stroke="#00A651"
          strokeWidth={2}
          fill="url(#trend)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function RiskDonut({ data }: { data: { low: number; medium: number; high: number } }) {
  const entries = [
    { name: 'Faible', value: data.low, color: '#00A651' },
    { name: 'Moyen', value: data.medium, color: '#E8A33D' },
    { name: 'Élevé', value: data.high, color: '#C0392B' },
  ].filter((e) => e.value > 0);
  const total = entries.reduce((s, e) => s + e.value, 0);

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={entries.length ? entries : [{ name: '—', value: 1, color: '#2a3a33' }]}
            dataKey="value"
            innerRadius={58}
            outerRadius={82}
            paddingAngle={2}
            stroke="none"
          >
            {(entries.length ? entries : [{ color: '#2a3a33' }]).map((e, i) => (
              <Cell key={i} fill={e.color} />
            ))}
          </Pie>
          <Tooltip {...tooltipStyle} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 grid place-items-center">
        <div className="text-center">
          <div className="font-display text-2xl font-bold text-white">{total}</div>
          <div className="text-[11px] text-sand/50">parcelles</div>
        </div>
      </div>
    </div>
  );
}
