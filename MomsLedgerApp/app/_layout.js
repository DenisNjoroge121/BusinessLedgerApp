import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { useRouter, Segment } from 'expo-router';
import { useAuthStore } from '../src/store/authStore';

export default function RootLayout() {
  const { isAuthenticated, token } = useAuthStore();
  const router = useRouter();
  const segment = useSegment();

  useEffect(() => {
    // AUTH LOGIC:
    // If not authenticated and not in the (auth) group, redirect to login
    const inAuthGroup = segment[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/(tabs)');
    }
  }, [isAuthenticated]);

  return (
    <Stack>
      {/* Hide the header for the main groups */}
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="customer/[id]" options={{ title: 'Customer Ledger' }} />
    </Stack>
  );
}
