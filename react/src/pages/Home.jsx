import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getTopListings, ingestByUrl, ListingKeys } from '../api/listings';

function formatPrice(priceStr) {
  if (!priceStr && priceStr !== '0') return '';
  const num = Number(priceStr);
  if (Number.isNaN(num)) return String(priceStr || '').trim();
  return num.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 });
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });
}

export default function Home() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');

  const listingsQuery = useQuery({
    queryKey: ListingKeys.list(20),
    queryFn: () => getTopListings(20),
  });

  const ingestMutation = useMutation({
    mutationFn: (val) => ingestByUrl(val),
    onSuccess: (data) => {
      if (data && data.id) {
        navigate(`/ad/${data.id}`);
      }
    },
  });

  const onSubmit = (e) => {
    e.preventDefault();
    const trimmed = (url || '').trim();
    if (!trimmed) return;
    ingestMutation.mutate(trimmed);
  };

  return (
    <div className="space-y-10" data-easytag="id1-react/src/pages/Home.jsx">
      <section className="text-center" data-easytag="id2-react/src/pages/Home.jsx">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight" data-easytag="id3-react/src/pages/Home.jsx">Авитолог</h1>
        <p className="mt-2 text-gray-600" data-easytag="id4-react/src/pages/Home.jsx">Комментируйте объявления с Avito. Минималистично. По‑яблочному.</p>

        <form onSubmit={onSubmit} className="mt-6 mx-auto max-w-2xl flex items-stretch gap-3" data-easytag="id5-react/src/pages/Home.jsx">
          <input
            data-easytag="id6-react/src/pages/Home.jsx"
            type="url"
            inputMode="url"
            className="flex-1 rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-400 transition bg-white"
            placeholder="Вставьте ссылку на объявление avito.ru"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={ingestMutation.isPending}
          />
          <button
            data-easytag="id7-react/src/pages/Home.jsx"
            type="submit"
            className="rounded-xl bg-black text-white px-5 py-3 font-medium hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={ingestMutation.isPending}
          >
            {ingestMutation.isPending ? 'Открываем…' : 'Открыть'}
          </button>
        </form>
        {ingestMutation.isError && (
          <p className="mt-3 text-sm text-red-600" data-easytag="id8-react/src/pages/Home.jsx">Не удалось обработать ссылку. Проверьте корректность и попробуйте ещё раз.</p>
        )}
      </section>

      <section className="space-y-4" data-easytag="id9-react/src/pages/Home.jsx">
        <div className="flex items-center justify-between" data-easytag="id10-react/src/pages/Home.jsx">
          <h2 className="text-xl font-semibold" data-easytag="id11-react/src/pages/Home.jsx">Самые просматриваемые</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-easytag="id12-react/src/pages/Home.jsx">
          {listingsQuery.isLoading && (
            <div className="col-span-full text-center text-gray-500" data-easytag="id13-react/src/pages/Home.jsx">Загрузка…</div>
          )}

          {listingsQuery.isError && (
            <div className="col-span-full text-center text-red-600" data-easytag="id14-react/src/pages/Home.jsx">Ошибка загрузки объявлений</div>
          )}

          {Array.isArray(listingsQuery.data) && listingsQuery.data.map((item) => (
            <Link
              to={`/ad/${item.id}`}
              key={item.id}
              className="group block rounded-2xl border border-gray-200 overflow-hidden hover:shadow-sm transition bg-white"
              data-easytag="id15-react/src/pages/Home.jsx"
            >
              <div className="aspect-[4/3] bg-gray-100 overflow-hidden" data-easytag="id16-react/src/pages/Home.jsx">
                {item.image_url ? (
                  <img src={item.image_url} alt={item.title} className="w-full h-full object-cover group-hover:scale-[1.02] transition" data-easytag="id17-react/src/pages/Home.jsx" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400" data-easytag="id18-react/src/pages/Home.jsx">Изображение недоступно</div>
                )}
              </div>
              <div className="p-4 space-y-2" data-easytag="id19-react/src/pages/Home.jsx">
                <h3 className="text-base font-medium line-clamp-2" data-easytag="id20-react/src/pages/Home.jsx">{item.title}</h3>
                <p className="text-sm text-gray-900" data-easytag="id21-react/src/pages/Home.jsx">{formatPrice(item.price)}</p>
                <p className="text-xs text-gray-500" data-easytag="id22-react/src/pages/Home.jsx">{formatDate(item.published_at)}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
