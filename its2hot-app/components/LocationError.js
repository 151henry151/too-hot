import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const LocationError = ({ 
  errorType = 'permission', 
  onRetry, 
  onOpenSettings 
}) => {
  const getErrorContent = () => {
    switch (errorType) {
      case 'permission':
        return {
          icon: 'location-outline',
          title: 'Location Permission Required',
          message: 'This app needs location access to provide accurate temperature alerts for your area.',
          actionText: 'Open Settings',
          action: onOpenSettings || (() => {
            Alert.alert(
              'Location Permission',
              'Please enable location access in your device settings to get temperature alerts.',
              [
                { text: 'Cancel', style: 'cancel' },
                { 
                  text: 'Open Settings', 
                  onPress: () => Linking.openSettings() 
                }
              ]
            );
          })
        };
      case 'gps':
        return {
          icon: 'location-off-outline',
          title: 'GPS Signal Weak',
          message: 'Unable to get your location. Please check your GPS settings and try again.',
          actionText: 'Try Again',
          action: onRetry
        };
      case 'timeout':
        return {
          icon: 'time-outline',
          title: 'Location Timeout',
          message: 'Getting your location took too long. Please try again.',
          actionText: 'Try Again',
          action: onRetry
        };
      default:
        return {
          icon: 'location-outline',
          title: 'Location Error',
          message: 'Unable to get your location. Please try again.',
          actionText: 'Try Again',
          action: onRetry
        };
    }
  };

  const content = getErrorContent();

  return (
    <View style={styles.container}>
      <View style={styles.errorContainer}>
        <Ionicons name={content.icon} size={48} color="#6b7280" />
        <Text style={styles.title}>{content.title}</Text>
        <Text style={styles.message}>{content.message}</Text>
        
        {content.action && (
          <TouchableOpacity style={styles.actionButton} onPress={content.action}>
            <Ionicons name="settings-outline" size={20} color="white" />
            <Text style={styles.actionButtonText}>{content.actionText}</Text>
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
    marginBottom: 20,
  },
  actionButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default LocationError; 