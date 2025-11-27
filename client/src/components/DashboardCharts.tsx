import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, LineChart, Line } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { MapContainerProps } from 'react-leaflet';

const statusColors: Record<string, string> = {
  'on_time': '#22c55e',
  'at_risk': '#f59e42',
  'delayed': '#ef4444',
  'default': '#0ea5e9',
};

export function ProfitMarginChart({ data }: { data: { gross: number, net: number } }) {
  const chartData = [
    { name: 'Gross', value: data.gross },
    { name: 'Net', value: data.net },
  ];
  const COLORS = ['#22c55e', '#0ea5e9'];
  return (
    <ResponsiveContainer width="100%" height={120}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={40} label>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function BudgetTrendChart({ data }: { data: Array<{ month: string, budget: number, actual: number, earned: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="budget" stroke="#0ea5e9" name="Budget" />
        <Line type="monotone" dataKey="actual" stroke="#22c55e" name="Actual" />
        <Line type="monotone" dataKey="earned" stroke="#f59e42" name="Earned Value" />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Implementing ProjectPortfolioMap using react-leaflet
export function ProjectPortfolioMap({ data }: { data: Array<{ site_id: string, lat: number, lng: number, status: string, name?: string }> }) {
  const center: [number, number] = data.length ? [data[0].lat, data[0].lng] : [-28.4793, 24.6727]; // South Africa center
  return (
    <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {data.map((site) => (
        <Marker
          key={site.site_id}
          position={[site.lat, site.lng] as [number, number]}
          icon={L.divIcon({
            className: 'custom-marker',
            html: `<div style='background:${statusColors[site.status] || statusColors.default};width:18px;height:18px;border-radius:50%;border:2px solid #fff;'></div>`
          }) as L.Icon}
        >
          <Popup>
            <strong>{site.name || site.site_id}</strong><br />
            Status: {site.status}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
