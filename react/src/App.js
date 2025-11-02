import ErrorBoundary from './ErrorBoundary';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import AdPage from './pages/AdPage';
import NotFound from './pages/NotFound';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-white text-ink font-sans" data-easytag="id1-react/src/App.js">
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur shadow-subtle" data-easytag="id2-react/src/App.js">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 py-3 flex items-center justify-between" data-easytag="id3-react/src/App.js">
            <Link to="/" className="text-[17px] font-semibold tracking-tight text-ink hover:opacity-80 transition" data-easytag="id4-react/src/App.js">Авитолог</Link>
            <nav className="flex items-center gap-6" data-easytag="id5-react/src/App.js">
              <a href="/" className="text-sm text-ink-dim hover:text-ink transition" data-easytag="id6-react/src/App.js">Главная</a>
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-6xl px-4 sm:px-6 py-10" data-easytag="id7-react/src/App.js">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/ad/:id" element={<AdPage />} />
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        <footer className="border-t border-gray-100 py-6" data-easytag="id8-react/src/App.js">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 text-xs text-ink-dim" data-easytag="id9-react/src/App.js">
            <p data-easytag="id10-react/src/App.js">© {new Date().getFullYear()} Авитолог. Сделано с вниманием к деталям.</p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
