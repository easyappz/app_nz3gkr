import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center" data-easytag="id1-react/src/pages/NotFound.jsx">
      <h1 className="text-6xl font-semibold text-ink" data-easytag="id2-react/src/pages/NotFound.jsx">404</h1>
      <p className="mt-3 text-ink-dim" data-easytag="id3-react/src/pages/NotFound.jsx">Страница не найдена</p>
      <Link to="/" className="mt-6 rounded-lg bg-black text-white text-sm font-medium px-4 py-2 hover:bg-ink-light active:opacity-90 transition" data-easytag="id4-react/src/pages/NotFound.jsx">На главную</Link>
    </div>
  );
}

export default NotFound;
