import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import apiClient from "../../src/api/client";
import { MoneyMath } from "../../src/utils/math";

export default function CategoryDetail() {
  const { id } = useLocalSearchParams(); // Gets the category ID from the URL
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [showBalances, setShowBalances] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      // 1. Fetch Category Details
      const catRes = await apiClient.get(`/categories/${id}/`);
      setCategory(catRes.data);

      // 2. Fetch Customers for this specific category
      const custRes = await apiClient.get(`/customers/?category=${id}`);
      setCustomers(custRes.data);
    } catch (error) {
      console.error("Error fetching category details:", error);
    } finally {
      setLoading(false);
    }
  };

  const maskMoney = (amount) => {
    return showBalances ? MoneyMath.format(amount) : "••••••";
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1A237E" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Custom Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#1A237E" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{category?.name}</Text>
        <TouchableOpacity
          style={styles.privacyBtn}
          onPress={() => setShowBalances(!showBalances)}
        >
          <Ionicons
            name={showBalances ? "eye-off" : "eye"}
            size={22}
            color="#1A237E"
          />
        </TouchableOpacity>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Category Summary Tile */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>
            Total Outstanding in {category?.name}
          </Text>
          <Text style={styles.summaryValue}>{maskMoney(45000.0)}</Text>
          {/* Note: In production, we would sum customers' current_balance here */}
        </View>

        {/* Customer List */}
        <View style={styles.listSection}>
          <View style={styles.listHeader}>
            <Text style={styles.listTitle}>Customers</Text>
            <Text style={styles.customerCount}>{customers.length} Total</Text>
          </View>

          {customers.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>
                No customers found in this category.
              </Text>
            </View>
          ) : (
            customers.map((cust) => (
              <TouchableOpacity
                key={cust.id}
                style={styles.customerCard}
                onPress={() => router.push(`/customer/${cust.id}`)}
              >
                <View style={styles.custInfo}>
                  <Text style={styles.custName}>{cust.name}</Text>
                  <Text style={styles.custPhone}>
                    {cust.phone || "No phone"}
                  </Text>
                </View>
                <View style={styles.custBalanceContainer}>
                  <Text style={styles.custBalance}>
                    {maskMoney(cust.current_balance)}
                  </Text>
                  <Ionicons name="chevron-forward" size={16} color="#CCC" />
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8F9FA" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: "#fff",
    elevation: 2,
  },
  backBtn: { padding: 5 },
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#1A237E" },
  privacyBtn: {
    backgroundColor: "#F1F3F5",
    padding: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  summaryCard: {
    backgroundColor: "#1A237E",
    margin: 20,
    padding: 25,
    borderRadius: 20,
    alignItems: "center",
    elevation: 5,
  },
  summaryLabel: { color: "#C5CAE9", fontSize: 14, marginBottom: 10 },
  summaryValue: { color: "#fff", fontSize: 28, fontWeight: "bold" },
  listSection: { paddingHorizontal: 20 },
  listHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 15,
  },
  listTitle: { fontSize: 18, fontWeight: "bold", color: "#333" },
  customerCount: { fontSize: 14, color: "#666" },
  customerCard: {
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 15,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
    elevation: 1,
    borderWidth: 1,
    borderColor: "#F1F3F5",
  },
  custInfo: { flex: 1 },
  custName: { fontSize: 16, fontWeight: "600", color: "#333" },
  custPhone: { fontSize: 13, color: "#888", marginTop: 2 },
  custBalanceContainer: { flexDirection: "row", alignItems: "center" },
  custBalance: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#1A237E",
    marginRight: 10,
  },
  emptyState: { alignItems: "center", marginTop: 50 },
  emptyText: { color: "#999", fontSize: 16 },
});
