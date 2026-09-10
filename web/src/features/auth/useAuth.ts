import { create } from 'zustand';
import { api, tokenStore } from '@/lib/api';
import type { Role, TokenResponse, User } from '@/types/api';

type Status = 'idle' | 'loading' | 'authed' | 'anon';

interface AuthState {
  user: User | null;
  status: Status;
  bootstrap: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: Role[]) => boolean;
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  status: 'idle',

  bootstrap: async () => {
    if (!tokenStore.access) {
      set({ status: 'anon' });
      return;
    }
    set({ status: 'loading' });
    try {
      const user = await api<User>('/auth/me');
      set({ user, status: 'authed' });
    } catch {
      tokenStore.clear();
      set({ user: null, status: 'anon' });
    }
  },

  login: async (email, password) => {
    const res = await api<TokenResponse>('/auth/login', {
      method: 'POST',
      auth: false,
      body: { email, password },
    });
    tokenStore.set(res.access_token, res.refresh_token);
    const user = await api<User>('/auth/me');
    set({ user, status: 'authed' });
  },

  logout: () => {
    tokenStore.clear();
    set({ user: null, status: 'anon' });
  },

  hasRole: (...roles) => {
    const role = get().user?.role;
    if (!role) return false;
    return role === 'admin' || roles.includes(role);
  },
}));
