import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

const History = () => {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getAll(0, 50)
      .then(data => {
        setRuns(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Evaluation History</h2>
      
      <div className="glass-card overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-400 text-sm uppercase tracking-wider">
              <th className="p-4">ID</th>
              <th className="p-4">Provider</th>
              <th className="p-4">Tokens Saved</th>
              <th className="p-4">Compression</th>
              <th className="p-4">Latency</th>
              <th className="p-4">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="p-8 text-center text-gray-500">Loading...</td></tr>
            ) : runs.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-gray-500">No evaluations found.</td></tr>
            ) : (
              runs.map(run => (
                <tr 
                  key={run.id} 
                  onClick={() => navigate(`/evaluation/${run.id}`)}
                  className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <td className="p-4 text-primary font-medium">#{run.id}</td>
                  <td className="p-4 capitalize">{run.provider}</td>
                  <td className="p-4 text-green-400">+{run.token_saved}</td>
                  <td className="p-4">{(run.compression_ratio * 100).toFixed(1)}%</td>
                  <td className="p-4">{(run.total_latency * 1000).toFixed(0)} ms</td>
                  <td className="p-4 text-gray-400 text-sm">{new Date(run.timestamp).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default History;
