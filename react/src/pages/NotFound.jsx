import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center" data-easytag="id1-react/src/pages/NotFound.jsx">
      <h1 className="text-6xl font-semibold tracking-tight" data-easytag="id2-react/src/pages/NotFound.jsx">404</h1>
      <p className="mt-3 text-lg text-gray-600" data-easytag="id3-react/src/pages/NotFound.jsx">Страница не найдена</p>
      <Link to="/" className="mt-6 rounded-xl bg-black text-white px-5 py-3 text-sm hover:bg-gray-900" data-easytag="id4-react/src/pages/NotFound.jsx">
        На главную
      </Link>
    </div>
  );
}
