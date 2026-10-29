import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, View, Text, ScrollView, 
  TouchableOpacity, ActivityIndicator, FlatList 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../src/api/client';
import { MoneyMath } from '../../src/utils/math';
import { useRouter } from 'expo-router';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [showBalances, setShowBalances] = useState(false); // Privacy Toggle
  const router = useRouter();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await apiClient.get('/categories/');
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    } finally {
      setLoading(false);
    }
  };

  // Helper to mask money for privacy
  const maskMoney = (amount) => {
    return showBalances ? MoneyMath.format(amount) : '••••••';
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1A237E" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header Section */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, Mom! 👋</Text>
          <Text style={styles.dateText}>Here is your business overview</Text>
        </View>
        <TouchableOpacity 
          style={styles.privacyBtn} 
          onPress={() => setShowBalances(!showBalances)}
        >
          <Ionicons 
            name={showBalances ? "eye-off" : "eye"} 
            size={24} 
            color="#1A237E" 
          />
        </TouchableOpacity>
      </View>

      {/* Financial Summary Tiles */}
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: '#E8EAF6' }]}>
          <Text style={styles.statLabel}>Total Pending</Text>
          <Text style={styles.statValue}>{maskMoney(12500.50)}</Text> 
          {/* In real app, calculate sum from categories */}
        </View>
        <View style={[styles.statCard, { backgroundColor: '#E8F5E9' }]}>
          <Text style={styles.statLabel}>Collected Today</Text>
          <Text style={styles.statValue}>{maskMoney(1200.00)}</Text>
        </View>
      </View>

      {/* Categories List */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Businesses</Text>
        <View style={styles.categoryGrid}>
          {categories.map((cat) => (
            <TouchableOpacity 
              key={cat.id} 
              style={styles.categoryCard}
              onPress={() => router.push(`/category/${cat.id}`)}
            >
              <Text style={styles.catIcon}>{cat.icon || '📦'}</Text>
              <Text style={styles.catName}>{cat.name}</Text>
              <Text style={styles.catBalance}>{maskMoney(500.00)}</Text>
              <Ionicons name="chevron-forward" size={16} color="#CCC" />
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F9FA', padding: 20 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginTop: 40, 
    marginBottom: 30 
  },
  greeting: { fontSize: 24, fontWeight: 'bold', color: '#1A237E' },
  dateText: { fontSize: 14, color: '#666' },
  privacyBtn: { 
    backgroundColor: '#fff', 
    padding: 10, 
    borderRadius: 12, 
    elevation: 2, 
    borderWidth: 1, 
    borderColor: '#E0E0E0' 
  },
  statsContainer: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    marginBottom: 30 
  },
  statCard: { 
    width: '48%', 
    padding: 20, 
    borderRadius: 15, 
    alignItems: 'center' 
  },
  statLabel: { fontSize: 13, color: '#555', marginBottom: 5 },
  statValue: { fontSize: 18, fontWeight: 'bold', color: '#1A237E' },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 15 },
  categoryGrid: { gap: 15 },
  categoryCard: { 
    backgroundColor: '#fff', 
    padding: 15, 
    borderRadius: 15, 
    flexDirection: 'row', 
    alignItems: 'center',
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F1F3F5'
  },
  catIcon: { fontSize: 24, marginRight: 15 },
  catName: { flex: 1, fontSize: 16, fontWeight: '600', color: '#333' },
  catBalance: { fontSize: 16, fontWeight: 'bold', color: '#1A237E', marginRight: 10 },
});
