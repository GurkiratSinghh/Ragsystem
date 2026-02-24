import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import './index.css';

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <ChatInterface />
      </main>
    </div>
  );
}
