import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { login, register } from '../api/auth';

export default function AuthModal({ isOpen, mode = 'login', onClose, onSuccess }) {
  const [currentMode, setCurrentMode] = useState(mode);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    setCurrentMode(mode);
  }, [mode]);

  const loginMutation = useMutation({
    mutationFn: ({ username, password }) => login({ username, password }),
  });

  const registerMutation = useMutation({
    mutationFn: ({ username, password, email }) => register({ username, password, email }),
  });

  const isPending = loginMutation.isPending || registerMutation.isPending;
  const errorObj = loginMutation.isError ? loginMutation.error : (registerMutation.isError ? registerMutation.error : null);

  const resetForm = () => {
    setUsername('');
    setPassword('');
    setEmail('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const u = (username || '').trim();
    const p = (password || '').trim();
    const m = (email || '').trim();
    if (!u || !p) return;

    try {
      const data = currentMode === 'login'
        ? await loginMutation.mutateAsync({ username: u, password: p })
        : await registerMutation.mutateAsync({ username: u, password: p, email: m || undefined });

      if (data?.token) {
        localStorage.setItem('token', data.token);
      }
      resetForm();
      if (typeof onSuccess === 'function') onSuccess();
      if (typeof onClose === 'function') onClose();
    } catch (e2) {
      // handled by axios interceptor globally
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" aria-modal="true" role="dialog" data-easytag="id1-react/src/components/AuthModal.jsx">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} data-easytag="id2-react/src/components/AuthModal.jsx"></div>
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl" data-easytag="id3-react/src/components/AuthModal.jsx">
        <div className="flex items-center justify-between" data-easytag="id4-react/src/components/AuthModal.jsx">
          <h3 className="text-lg font-semibold" data-easytag="id5-react/src/components/AuthModal.jsx">{currentMode === 'login' ? 'Вход' : 'Регистрация'}</h3>
          <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-800" aria-label="Закрыть" data-easytag="id6-react/src/components/AuthModal.jsx">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3" data-easytag="id7-react/src/components/AuthModal.jsx">
          <div className="space-y-1" data-easytag="id8-react/src/components/AuthModal.jsx">
            <label className="text-sm text-gray-700" htmlFor="auth-username" data-easytag="id9-react/src/components/AuthModal.jsx">Логин</label>
            <input
              id="auth-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-gray-200 px-4 py-2 outline-none focus:border-gray-400"
              placeholder="ivan"
              data-easytag="id10-react/src/components/AuthModal.jsx"
            />
          </div>
          <div className="space-y-1" data-easytag="id11-react/src/components/AuthModal.jsx">
            <label className="text-sm text-gray-700" htmlFor="auth-password" data-easytag="id12-react/src/components/AuthModal.jsx">Пароль</label>
            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-gray-200 px-4 py-2 outline-none focus:border-gray-400"
              placeholder="••••••••"
              data-easytag="id13-react/src/components/AuthModal.jsx"
            />
          </div>
          {currentMode === 'register' && (
            <div className="space-y-1" data-easytag="id14-react/src/components/AuthModal.jsx">
              <label className="text-sm text-gray-700" htmlFor="auth-email" data-easytag="id15-react/src/components/AuthModal.jsx">Email (необязательно)</label>
              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-gray-200 px-4 py-2 outline-none focus:border-gray-400"
                placeholder="ivan@example.com"
                data-easytag="id16-react/src/components/AuthModal.jsx"
              />
            </div>
          )}

          {errorObj && (
            <div className="text-sm text-red-600" data-easytag="id17-react/src/components/AuthModal.jsx">Ошибка авторизации. Проверьте данные.</div>
          )}

          <button
            type="submit"
            className="w-full rounded-xl bg-black text-white px-5 py-2 font-medium hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isPending}
            data-easytag="id18-react/src/components/AuthModal.jsx"
          >
            {isPending ? 'Подождите…' : (currentMode === 'login' ? 'Войти' : 'Зарегистрироваться')}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600" data-easytag="id19-react/src/components/AuthModal.jsx">
          {currentMode === 'login' ? (
            <p data-easytag="id20-react/src/components/AuthModal.jsx">
              Нет аккаунта?{' '}
              <button type="button" className="underline underline-offset-2 hover:text-gray-900" onClick={() => setCurrentMode('register')} data-easytag="id21-react/src/components/AuthModal.jsx">Зарегистрируйтесь</button>
            </p>
          ) : (
            <p data-easytag="id22-react/src/components/AuthModal.jsx">
              Уже есть аккаунт?{' '}
              <button type="button" className="underline underline-offset-2 hover:text-gray-900" onClick={() => setCurrentMode('login')} data-easytag="id23-react/src/components/AuthModal.jsx">Войдите</button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
