import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const NetworkError = ({ 
  message = "No internet connection", 
  onRetry, 
  showRetry = true,
  customMessage 
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.errorContainer}>
        <Ionicons name="wifi-outline" size={48} color="#6b7280" />
        <Text style={styles.title}>Connection Error</Text>
        <Text style={styles.message}>
          {customMessage || message}
        </Text>
        <Text style={styles.subtitle}>
          Please check your internet connection and try again.
        </Text>
        
        {showRetry && onRetry && (
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Ionicons name="refresh" size={20} color="white" />
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        )}
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
  errorContainer: {
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
    maxWidth: 300,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default NetworkError; 