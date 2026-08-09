import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { api } from '../api/client';

const EvaluationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [run, setRun] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      api.getById(id)
        .then(data => {
          setRun(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) return <div className="p-8">Loading details...</div>;
  if (!run) return <div className="p-8 text-red-500">Evaluation not found.</div>;

  return (
    <div className="space-y-6">
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft size={16} /> Back to History
      </button>

      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Evaluation #{run.id}</h2>
        <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium capitalize">
          {run.provider}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <div className="text-gray-400 text-sm">Latency</div>
          <div className="text-xl font-bold">{(run.total_latency * 1000).toFixed(0)} ms</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-gray-400 text-sm">Compression</div>
          <div className="text-xl font-bold">{(run.compression_ratio * 100).toFixed(1)}%</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-gray-400 text-sm">Tokens Saved</div>
          <div className="text-xl font-bold text-green-400">+{run.token_saved}</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-gray-400 text-sm">Memories Used</div>
          <div className="text-xl font-bold">{run.selected_memories}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6 flex flex-col h-[500px]">
          <h3 className="text-lg font-medium mb-4 text-gray-300">Original Query</h3>
          <div className="flex-1 bg-background border border-white/10 rounded-lg p-4 overflow-y-auto whitespace-pre-wrap font-mono text-sm">
            {run.query}
          </div>
        </div>
        
        <div className="glass-card p-6 flex flex-col h-[500px]">
          <h3 className="text-lg font-medium mb-4 text-primary">Contextual Analytics</h3>
          <div className="flex-1 overflow-y-auto space-y-4">
            <div className="bg-background border border-white/10 rounded-lg p-4">
              <div className="text-xs text-gray-500 uppercase mb-2">Original Context Tokens</div>
              <div className="text-2xl font-bold">{run.original_tokens}</div>
            </div>
            <div className="bg-background border border-white/10 rounded-lg p-4">
              <div className="text-xs text-gray-500 uppercase mb-2">Compressed Context Tokens</div>
              <div className="text-2xl font-bold text-primary">{run.compressed_tokens}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationDetail;
