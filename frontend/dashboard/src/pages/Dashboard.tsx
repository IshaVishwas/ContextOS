import { useEffect, useState } from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  BarChart, Bar, PieChart, Pie, Cell 
} from 'recharts';
import { Zap, Timer, FileDigit, Database } from 'lucide-react';
import { api } from '../api/client';

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b'];

const Dashboard = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        const statusStr = err.response?.status ? `HTTP ${err.response.status}` : '';
        const detailStr = err.response?.data?.detail || err.message || 'Failed to fetch stats';
        setError(statusStr ? `${statusStr}: ${detailStr}` : detailStr);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="flex h-64 items-center justify-center text-primary">Loading metrics...</div>;
  if (error) return <div className="p-4 bg-red-500/10 border border-red-500 text-red-500 rounded-xl">{error}</div>;
  if (!stats || stats.status === 'no_data') return <div className="p-8 text-center text-gray-400">No evaluation statistics available yet. Run evaluation benchmarks or chat turns to populate stats.</div>;

  // Extract stats safely whether nested in averages or top level
  const totalEvaluations = stats.total_runs ?? stats.total_evaluations ?? 0;
  const avgCompression = stats.averages?.compression_ratio ?? stats.average_compression_ratio ?? 0;
  const avgTokensSaved = stats.averages?.tokens_saved_per_turn ?? stats.average_tokens_saved ?? 0;
  const avgLatency = (stats.averages?.latency_ms?.total ? stats.averages.latency_ms.total / 1000 : stats.average_latency) ?? 0;

  // Transform data for charts
  const providerData = Object.entries(stats.provider_distribution || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Optimization Overview</h2>
      
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <FileDigit size={18} />
            <span className="text-sm font-medium uppercase tracking-wider">Total Runs</span>
          </div>
          <span className="text-4xl font-bold text-white">{totalEvaluations}</span>
        </div>
        
        <div className="glass-card p-6 flex flex-col gap-2 relative overflow-hidden">
          <div className="flex items-center gap-2 text-gray-400">
            <Zap size={18} className="text-primary" />
            <span className="text-sm font-medium uppercase tracking-wider">Avg Compression</span>
          </div>
          <span className="text-4xl font-bold text-white">{(avgCompression * 100).toFixed(1)}%</span>
          <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-primary/20 rounded-full blur-2xl" />
        </div>

        <div className="glass-card p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <Database size={18} className="text-secondary" />
            <span className="text-sm font-medium uppercase tracking-wider">Avg Tokens Saved</span>
          </div>
          <span className="text-4xl font-bold text-white">{Math.round(Number(avgTokensSaved))}</span>
        </div>

        <div className="glass-card p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <Timer size={18} className="text-green-500" />
            <span className="text-sm font-medium uppercase tracking-wider">Avg Latency</span>
          </div>
          <span className="text-4xl font-bold text-white">{(avgLatency * 1000).toFixed(0)} ms</span>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-lg font-medium mb-6">Provider Distribution</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={providerData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                <XAxis dataKey="name" stroke="#888" />
                <YAxis stroke="#888" />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#171717', borderColor: '#333', borderRadius: '8px' }} 
                  cursor={{fill: '#2a2a2a'}} 
                />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="glass-card p-6">
          <h3 className="text-lg font-medium mb-6">Usage by Provider</h3>
          <div className="h-72 w-full flex justify-center items-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={providerData}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {providerData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#171717', borderColor: '#333', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 text-sm mt-4">
            {providerData.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <span className="text-gray-300 capitalize">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
