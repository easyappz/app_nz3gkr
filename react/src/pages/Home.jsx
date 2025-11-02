import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [value, setValue] = useState('');
  const navigate = useNavigate();

  const handleOpen = () => {
    if (!value) return;
    // Placeholder: Later will parse/resolve ID via backend. For now navigate to a stub path.
    navigate('/ad/new');
  };

  return (
    <div className="space-y-10" data-easytag="id1-react/src/pages/Home.jsx">
      <section className="flex flex-col items-start gap-6" data-easytag="id2-react/src/pages/Home.jsx">
        <h1 className="text-4xl sm:text-5xl tracking-tight font-semibold text-ink" data-easytag="id3-react/src/pages/Home.jsx">Авитолог</h1>
        <p className="text-base sm:text-lg text-ink-dim max-w-2xl" data-easytag="id4-react/src/pages/Home.jsx">Сервис для комментирования объявлений с Авито. Минимализм, скорость и удобство — как на сайте Apple.</p>
        <div className="w-full max-w-2xl rounded-xl border border-gray-200 shadow-subtle p-3 sm:p-4 bg-white" data-easytag="id5-react/src/pages/Home.jsx">
          <label className="block text-xs uppercase tracking-wide text-ink-dim mb-2" data-easytag="id6-react/src/pages/Home.jsx">Ссылка на объявление Авито</label>
          <div className="flex items-center gap-2" data-easytag="id7-react/src/pages/Home.jsx">
            <input
              data-easytag="id8-react/src/pages/Home.jsx"
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="Вставьте ссылку..."
              className="flex-1 appearance-none outline-none rounded-lg border border-gray-200 bg-white px-3 py-2 text-[15px] text-ink placeholder:text-gray-400 focus:border-gray-300 focus:ring-0"
            />
            <button
              data-easytag="id9-react/src/pages/Home.jsx"
              onClick={handleOpen}
              className="rounded-lg bg-black text-white text-sm font-medium px-4 py-2 hover:bg-ink-light active:opacity-90 transition"
            >Открыть</button>
          </div>
        </div>
      </section>

      <section className="space-y-4" data-easytag="id10-react/src/pages/Home.jsx">
        <h2 className="text-xl font-semibold text-ink" data-easytag="id11-react/src/pages/Home.jsx">Самые просматриваемые</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-easytag="id12-react/src/pages/Home.jsx">
          {/* Placeholder cards (empty spaces for future images) */}
          {[1,2,3,4,5,6].map((i) => (
            <div key={i} className="group rounded-xl border border-gray-200 bg-white p-4 shadow-subtle hover:shadow transition" data-easytag={`id13-${'react/src/pages/Home.jsx'}`}>
              <div className="aspect-video w-full rounded-lg bg-gray-50" data-easytag={`id14-${'react/src/pages/Home.jsx'}`} />
              <div className="mt-3 space-y-2" data-easytag={`id15-${'react/src/pages/Home.jsx'}`}>
                <div className="h-5 w-5/6 bg-gray-100 rounded" data-easytag={`id16-${'react/src/pages/Home.jsx'}`}></div>
                <div className="h-4 w-1/3 bg-gray-100 rounded" data-easytag={`id17-${'react/src/pages/Home.jsx'}`}></div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Home;
