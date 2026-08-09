import { useState } from 'react';
import { updateApiBaseUrl } from '../api/client';

const Settings = () => {
  const [url, setUrl] = useState(localStorage.getItem('contextos_backend_url') || 'http://127.0.0.1:8000');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('contextos_backend_url', url);
    updateApiBaseUrl(url);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-3xl font-bold">Settings</h2>
      
      <div className="glass-card p-6 space-y-6">
        <div>
          <h3 className="text-lg font-medium mb-2">Backend Connection</h3>
          <p className="text-sm text-gray-400 mb-4">Configure the ContextOS backend URL to connect the dashboard to your running FastAPI instance.</p>
          
          <div className="flex gap-4">
            <input 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 bg-background border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary transition-colors"
              placeholder="http://127.0.0.1:8000"
            />
            <button onClick={handleSave} className="btn-primary min-w-[100px]">
              {saved ? 'Saved!' : 'Save'}
            </button>
          </div>
        </div>

        <div className="pt-6 border-t border-white/5">
          <h3 className="text-lg font-medium mb-2">Theme Preferences</h3>
          <p className="text-sm text-gray-400 mb-4">ContextOS defaults to Dark Mode to reduce eye strain during deep work.</p>
          <div className="flex gap-4">
             <div className="px-4 py-2 bg-primary/20 text-primary border border-primary rounded-lg cursor-pointer">
               Dark Mode (Active)
             </div>
             <div className="px-4 py-2 bg-white/5 text-gray-500 border border-white/10 rounded-lg cursor-not-allowed">
               Light Mode (Coming Soon)
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
