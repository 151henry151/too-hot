import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const LoadingState = ({ 
  message = "Loading...", 
  showIcon = true,
  size = "large",
  color = "#3b82f6"
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.loadingContainer}>
        {showIcon && (
          <Ionicons name="thermometer-outline" size={48} color={color} style={styles.icon} />
        )}
        <ActivityIndicator size={size} color={color} style={styles.spinner} />
        <Text style={styles.message}>{message}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    maxWidth: 200,
  },
  icon: {
    marginBottom: 16,
  },
  spinner: {
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    fontWeight: '500',
  },
});

export default LoadingState; 