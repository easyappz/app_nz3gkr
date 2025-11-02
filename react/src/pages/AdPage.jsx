import { useParams } from 'react-router-dom';

function AdPage() {
  const { id } = useParams();

  return (
    <div className="space-y-8" data-easytag="id1-react/src/pages/AdPage.jsx">
      <header className="space-y-2" data-easytag="id2-react/src/pages/AdPage.jsx">
        <h1 className="text-3xl font-semibold tracking-tight text-ink" data-easytag="id3-react/src/pages/AdPage.jsx">Объявление</h1>
        <p className="text-sm text-ink-dim" data-easytag="id4-react/src/pages/AdPage.jsx">ID: {id}</p>
      </header>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8" data-easytag="id5-react/src/pages/AdPage.jsx">
        <div className="space-y-4" data-easytag="id6-react/src/pages/AdPage.jsx">
          <div className="aspect-video w-full rounded-xl bg-gray-50 border border-gray-200" data-easytag="id7-react/src/pages/AdPage.jsx" />
          <div className="h-10 w-2/3 bg-gray-100 rounded" data-easytag="id8-react/src/pages/AdPage.jsx"></div>
          <div className="h-4 w-1/3 bg-gray-100 rounded" data-easytag="id9-react/src/pages/AdPage.jsx"></div>
        </div>
        <div className="space-y-6" data-easytag="id10-react/src/pages/AdPage.jsx">
          <div className="space-y-2" data-easytag="id11-react/src/pages/AdPage.jsx">
            <div className="h-6 w-4/6 bg-gray-100 rounded" data-easytag="id12-react/src/pages/AdPage.jsx"></div>
            <div className="h-4 w-5/6 bg-gray-100 rounded" data-easytag="id13-react/src/pages/AdPage.jsx"></div>
            <div className="h-4 w-3/6 bg-gray-100 rounded" data-easytag="id14-react/src/pages/AdPage.jsx"></div>
          </div>
          <div className="rounded-xl border border-gray-200 p-4 bg-white shadow-subtle" data-easytag="id15-react/src/pages/AdPage.jsx">
            <h2 className="text-lg font-semibold text-ink mb-3" data-easytag="id16-react/src/pages/AdPage.jsx">Комментарии</h2>
            <div className="h-24 rounded-lg bg-gray-50 border border-dashed border-gray-200 flex items-center justify-center text-ink-dim" data-easytag="id17-react/src/pages/AdPage.jsx">Здесь будет форма и список комментариев</div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default AdPage;
