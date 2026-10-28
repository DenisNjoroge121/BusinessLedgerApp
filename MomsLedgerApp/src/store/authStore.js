import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: async (user, token) => {
        // Save token in encrypted storage for security
        await SecureStore.setItemAsync('user_token', token);
        set({ user, token, isAuthenticated: true });
      },

      logout: async () => {
        await SecureStore.deleteItemAsync('user_token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }), 
      // We don't persist the token in AsyncStorage; we fetch it from SecureStore on boot
    }
  )
);
