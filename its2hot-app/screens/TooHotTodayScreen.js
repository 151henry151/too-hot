import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';

function getOrdinal(n) {
  const s = ["th", "st", "nd", "rd"], v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export default function TooHotTodayScreen({ route }) {
  const navigation = useNavigation();
  const { location, current_temp, avg_temp } = route.params || {};
  const tempDiff = current_temp && avg_temp ? (current_temp - avg_temp).toFixed(1) : null;
  const today = new Date();
  const monthName = today.toLocaleString('default', { month: 'long' });
  const dayWithOrdinal = getOrdinal(today.getDate());

  return (
    <View style={styles.container}>
      {/* Top-left back button */}
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate('Home')}>
        <Text style={styles.backButtonText}>← Home</Text>
      </TouchableOpacity>
      <Text style={styles.title}>Today in {location || 'your area'}:</Text>
      {current_temp && (
        <Text style={styles.temp}>
          It is <Text style={styles.bold}>{current_temp}°F</Text> today.
        </Text>
      )}
      {tempDiff && avg_temp && (
        <Text style={styles.diff}>
          That's <Text style={styles.bold}>{tempDiff}°F hotter</Text> than the average temperature for {monthName} {dayWithOrdinal} ({avg_temp}°F)!
        </Text>
      )}
      <Text style={styles.subtitle}>
        Wear your "IT'S TOO HOT!" shirt to let everyone know that it's TOO HOT!
      </Text>
      <Image
        source={require('../assets/images/tshirt.png')}
        style={styles.tshirt}
        resizeMode="contain"
      />
      {/* Get Your Shirt button */}
      <TouchableOpacity style={styles.shopButton} onPress={() => navigation.navigate('Shop')}>
        <Text style={styles.shopButtonText}>Get Your Shirt</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#fff',
  },
  backButton: {
    position: 'absolute',
    top: 32,
    left: 16,
    zIndex: 10,
    padding: 8,
  },
  backButtonText: {
    fontSize: 18,
    color: '#1a1a1a',
    fontWeight: 'bold',
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#d7263d',
    textAlign: 'center',
    marginTop: 32,
  },
  temp: {
    fontSize: 22,
    marginBottom: 8,
    textAlign: 'center',
  },
  diff: {
    fontSize: 20,
    marginBottom: 16,
    color: '#d7263d',
    textAlign: 'center',
  },
  bold: {
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 24,
    textAlign: 'center',
  },
  tshirt: {
    width: 200,
    height: 200,
    marginBottom: 16,
  },
  shopButton: {
    backgroundColor: '#d7263d',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    marginTop: 8,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
}); 