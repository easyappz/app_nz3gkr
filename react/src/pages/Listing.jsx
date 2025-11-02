import React, { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getListing, ListingKeys } from '../api/listings';
import { getComments, addComment, deleteComment, CommentKeys } from '../api/comments';
import { me, AuthKeys } from '../api/auth';
import AuthModal from '../components/AuthModal';

function formatPrice(priceStr) {
  if (!priceStr && priceStr !== '0') return '';
  const num = Number(priceStr);
  if (Number.isNaN(num)) return String(priceStr || '').trim();
  return num.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 });
}

function formatDateTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function Listing() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const listingQuery = useQuery({
    queryKey: ListingKeys.detail(id),
    queryFn: () => getListing(id),
  });

  const commentsQuery = useQuery({
    queryKey: CommentKeys.list(id),
    queryFn: () => getComments(id),
  });

  const meQuery = useQuery({
    queryKey: AuthKeys.me,
    queryFn: me,
    enabled: Boolean(token),
    retry: 0,
  });

  const isAuthed = Boolean(token) && meQuery.data && meQuery.data.id;
  const canPost = isAuthed && !meQuery.data.is_blocked;

  const addMutation = useMutation({
    mutationFn: (text) => addComment(id, text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CommentKeys.list(id) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (commentId) => deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CommentKeys.list(id) });
    },
  });

  const [commentText, setCommentText] = useState('');
  const [authMode, setAuthMode] = useState(null); // 'login' | 'register' | null

  const canDeleteIds = useMemo(() => {
    const ids = new Set();
    if (!commentsQuery.data || !Array.isArray(commentsQuery.data)) return ids;
    const meObj = meQuery.data;
    for (const c of commentsQuery.data) {
      if (meObj && (meObj.is_staff || meObj.id === c.user_id)) {
        ids.add(c.id);
      }
    }
    return ids;
  }, [commentsQuery.data, meQuery.data]);

  const onSubmitComment = (e) => {
    e.preventDefault();
    const trimmed = (commentText || '').trim();
    if (!trimmed || addMutation.isPending) return;
    addMutation.mutate(trimmed, {
      onSuccess: () => setCommentText(''),
    });
  };

  return (
    <div className="space-y-10" data-easytag="id1-react/src/pages/Listing.jsx">
      {/* Listing details */}
      <section className="grid grid-cols-1 lg:grid-cols-5 gap-8" data-easytag="id2-react/src/pages/Listing.jsx">
        <div className="lg:col-span-3" data-easytag="id3-react/src/pages/Listing.jsx">
          <div className="aspect-[4/3] rounded-2xl bg-gray-100 overflow-hidden" data-easytag="id4-react/src/pages/Listing.jsx">
            {listingQuery.isLoading ? (
              <div className="w-full h-full flex items-center justify-center text-gray-400" data-easytag="id5-react/src/pages/Listing.jsx">Загрузка…</div>
            ) : listingQuery.data && listingQuery.data.image_url ? (
              <img src={listingQuery.data.image_url} alt={listingQuery.data.title} className="w-full h-full object-cover" data-easytag="id6-react/src/pages/Listing.jsx" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400" data-easytag="id7-react/src/pages/Listing.jsx">Изображение недоступно</div>
            )}
          </div>
        </div>
        <div className="lg:col-span-2 space-y-4" data-easytag="id8-react/src/pages/Listing.jsx">
          <h1 className="text-2xl font-semibold" data-easytag="id9-react/src/pages/Listing.jsx">
            {listingQuery.data ? listingQuery.data.title : '…'}
          </h1>
          <p className="text-xl" data-easytag="id10-react/src/pages/Listing.jsx">{listingQuery.data ? formatPrice(listingQuery.data.price) : ''}</p>
          <p className="text-sm text-gray-500" data-easytag="id11-react/src/pages/Listing.jsx">{listingQuery.data ? `Опубликовано: ${formatDateTime(listingQuery.data.published_at)}` : ''}</p>
          <div className="pt-2 text-gray-800 whitespace-pre-line" data-easytag="id12-react/src/pages/Listing.jsx">
            {listingQuery.data ? (listingQuery.data.description || 'Описание отсутствует') : ''}
          </div>
        </div>
      </section>

      {/* Comments */}
      <section className="space-y-6" data-easytag="id13-react/src/pages/Listing.jsx">
        <div className="flex items-center justify-between" data-easytag="id14-react/src/pages/Listing.jsx">
          <h2 className="text-xl font-semibold" data-easytag="id15-react/src/pages/Listing.jsx">Комментарии</h2>
          {!isAuthed && (
            <div className="flex gap-3" data-easytag="id16-react/src/pages/Listing.jsx">
              <button
                type="button"
                onClick={() => setAuthMode('login')}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm hover:bg-gray-50"
                data-easytag="id17-react/src/pages/Listing.jsx"
              >
                Войти
              </button>
              <button
                type="button"
                onClick={() => setAuthMode('register')}
                className="rounded-lg bg-black text-white px-4 py-2 text-sm hover:bg-gray-900"
                data-easytag="id18-react/src/pages/Listing.jsx"
              >
                Зарегистрироваться
              </button>
            </div>
          )}
        </div>

        {isAuthed && (
          <form onSubmit={onSubmitComment} className="space-y-3" data-easytag="id19-react/src/pages/Listing.jsx">
            {meQuery.data?.is_blocked && (
              <div className="text-sm text-red-600" data-easytag="id20-react/src/pages/Listing.jsx">Ваш аккаунт заблокирован. Вы не можете оставлять комментарии.</div>
            )}
            <textarea
              data-easytag="id21-react/src/pages/Listing.jsx"
              rows={3}
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-400 transition"
              placeholder="Напишите свой комментарий"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              disabled={!canPost || addMutation.isPending}
            />
            <div className="flex items-center justify-end" data-easytag="id22-react/src/pages/Listing.jsx">
              <button
                type="submit"
                className="rounded-xl bg-black text-white px-5 py-2 text-sm font-medium hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!canPost || addMutation.isPending || (commentText || '').trim().length === 0}
                data-easytag="id23-react/src/pages/Listing.jsx"
              >
                {addMutation.isPending ? 'Отправляем…' : 'Отправить'}
              </button>
            </div>
          </form>
        )}

        <div className="space-y-3" data-easytag="id24-react/src/pages/Listing.jsx">
          {commentsQuery.isLoading && (
            <p className="text-gray-500" data-easytag="id25-react/src/pages/Listing.jsx">Загрузка комментариев…</p>
          )}
          {commentsQuery.isError && (
            <p className="text-red-600" data-easytag="id26-react/src/pages/Listing.jsx">Не удалось загрузить комментарии</p>
          )}

          {Array.isArray(commentsQuery.data) && commentsQuery.data.length === 0 && (
            <p className="text-gray-500" data-easytag="id27-react/src/pages/Listing.jsx">Пока нет комментариев. Будьте первым!</p>
          )}

          <ul className="space-y-3" data-easytag="id28-react/src/pages/Listing.jsx">
            {Array.isArray(commentsQuery.data) && commentsQuery.data.map((c) => (
              <li key={c.id} className="rounded-2xl border border-gray-200 p-4 bg-white" data-easytag="id29-react/src/pages/Listing.jsx">
                <div className="flex items-start justify-between gap-3" data-easytag="id30-react/src/pages/Listing.jsx">
                  <div className="space-y-0.5" data-easytag="id31-react/src/pages/Listing.jsx">
                    <p className="text-sm font-medium" data-easytag="id32-react/src/pages/Listing.jsx">{c.user_username}</p>
                    <p className="text-xs text-gray-500" data-easytag="id33-react/src/pages/Listing.jsx">{formatDateTime(c.created_at)}</p>
                  </div>
                  {canDeleteIds.has(c.id) && (
                    <button
                      type="button"
                      onClick={() => deleteMutation.mutate(c.id)}
                      className="text-xs text-red-600 hover:text-red-700"
                      data-easytag="id34-react/src/pages/Listing.jsx"
                    >
                      Удалить
                    </button>
                  )}
                </div>
                <p className="mt-2 text-sm leading-relaxed" data-easytag="id35-react/src/pages/Listing.jsx">{c.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <AuthModal
        isOpen={Boolean(authMode)}
        mode={authMode || 'login'}
        onClose={() => setAuthMode(null)}
        onSuccess={async () => {
          await queryClient.invalidateQueries({ queryKey: AuthKeys.me });
          setAuthMode(null);
        }}
      />
    </div>
  );
}
