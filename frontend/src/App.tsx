import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Placeholder imports for pages
const Login = () => <div className="p-4 text-xl">Login Page</div>;
const Register = () => <div className="p-4 text-xl">Register Page</div>;
const Dashboard = () => <div className="p-4 text-xl">Dashboard Page</div>;
const Memory = () => <div className="p-4 text-xl">Memory Page</div>;
const Analytics = () => <div className="p-4 text-xl">Analytics Page</div>;
const Settings = () => <div className="p-4 text-xl">Settings Page</div>;
const Profile = () => <div className="p-4 text-xl">Profile Page</div>;

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <header className="bg-white shadow-sm p-4 font-bold text-xl border-b">
          ContextOS
        </header>
        <main className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/memory" element={<Memory />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
