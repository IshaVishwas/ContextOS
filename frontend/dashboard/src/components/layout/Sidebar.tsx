import { NavLink } from 'react-router-dom';
import { LayoutDashboard, History, Settings, BrainCircuit } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'History', path: '/history', icon: <History size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <aside className="w-64 border-r border-white/5 bg-surface/50 backdrop-blur-xl h-screen sticky top-0 flex flex-col">
      <div className="p-6 flex items-center gap-3">
        <div className="p-2 bg-primary/20 text-primary rounded-lg">
          <BrainCircuit size={24} />
        </div>
        <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          ContextOS
        </h1>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                isActive
                  ? 'bg-primary/10 text-primary border border-primary/20'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-white/5'
              }`
            }
          >
            {item.icon}
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-white/5">
        <div className="text-xs text-gray-500 text-center">
          v1.0.0 Evaluation Engine
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
