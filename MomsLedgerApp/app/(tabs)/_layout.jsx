import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ 
        tabBarActiveTintColor: '#1A237E', 
        headerStyle: { backgroundColor: '#1A237E' },
        headerTintColor: '#fff',
        tabBarStyle: { height: 60, paddingBottom: 10 }
    }}>
      <Tabs.Screen 
        name="index" 
        options={{ 
            title: 'Dashboard', 
            tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} /> 
        }} 
      />
      <Tabs.Screen 
        name="analytics" 
        options={{ 
            title: 'Analytics', 
            tabBarIcon: ({ color }) => <Ionicons name="bar-chart" size={24} color={color} /> 
        }} 
      />
      <Tabs.Screen 
        name="settings" 
        options={{ 
            title: 'Settings', 
            tabBarIcon: ({ color }) => <Ionicons name="settings" size={24} color={color} /> 
        }} 
      />
    </Tabs>
  );
}
