import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export function NdviSeries({
  series,
  lossDate,
}: {
  series: Array<{ date: string; ndvi: number }>;
  lossDate?: string | null;
}) {
  const data = series.map((p) => ({ ...p, label: p.date.slice(0, 7) }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -14 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 10, stroke: '#5b6b63' }}
          tickLine={false}
          axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
          minTickGap={24}
        />
        <YAxis
          domain={[0, 1]}
          tick={{ fontSize: 10, stroke: '#5b6b63' }}
          tickLine={false}
          axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
        />
        <Tooltip
          contentStyle={{
            background: '#0E211A',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 12,
            fontSize: 12,
            color: '#F4EAD5',
          }}
          formatter={(v: number) => [v.toFixed(3), 'NDVI']}
        />
        {lossDate && (
          <ReferenceLine
            x={lossDate.slice(0, 7)}
            stroke="#C0392B"
            strokeDasharray="4 3"
            label={{ value: 'perte', fill: '#C0392B', fontSize: 10, position: 'top' }}
          />
        )}
        <Line
          type="monotone"
          dataKey="ndvi"
          stroke="#00A651"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
