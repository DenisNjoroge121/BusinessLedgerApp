import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { useRouter, useSegments } from 'expo-router';
import { useAuthStore } from '../src/store/authStore';

export default function RootLayout() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    // Debugging: This will show in your terminal what the app thinks the current path is
    console.log('Current segments:', segments);

    const inAuthGroup = segments[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      // Force redirect to welcome if not logged in and not already in auth screens
      router.replace('/(auth)/welcome');
    } else if (isAuthenticated && inAuthGroup) {
      // Force redirect to dashboard if logged in but trying to access auth screens
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, segments]);

  return (
    <Stack screenOptions={{ headerShown: false }}>
      {/* 
          Instead of naming "(auth)", we just define the groups. 
          If the warning persists, we can remove these and just use the default.
      */}
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    </Stack>
  );
}
