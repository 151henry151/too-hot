import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const PaymentError = ({ 
  errorType = 'payment_failed', 
  onRetry, 
  onCancel,
  customMessage 
}) => {
  const getErrorContent = () => {
    switch (errorType) {
      case 'payment_failed':
        return {
          icon: 'card-outline',
          title: 'Payment Failed',
          message: customMessage || 'Your payment could not be processed. Please try again.',
          actionText: 'Try Again',
          action: onRetry
        };
      case 'network_error':
        return {
          icon: 'wifi-outline',
          title: 'Connection Error',
          message: 'Unable to process payment due to network issues. Please check your connection and try again.',
          actionText: 'Try Again',
          action: onRetry
        };
      case 'insufficient_funds':
        return {
          icon: 'wallet-outline',
          title: 'Insufficient Funds',
          message: 'Your payment method has insufficient funds. Please try a different payment method.',
          actionText: 'Try Different Method',
          action: onRetry
        };
      case 'card_declined':
        return {
          icon: 'card-outline',
          title: 'Card Declined',
          message: 'Your card was declined. Please check your card details or try a different payment method.',
          actionText: 'Try Again',
          action: onRetry
        };
      case 'cancelled':
        return {
          icon: 'close-circle-outline',
          title: 'Payment Cancelled',
          message: 'You cancelled the payment. No charges were made.',
          actionText: 'Try Again',
          action: onRetry
        };
      default:
        return {
          icon: 'card-outline',
          title: 'Payment Error',
          message: customMessage || 'An error occurred during payment. Please try again.',
          actionText: 'Try Again',
          action: onRetry
        };
    }
  };

  const content = getErrorContent();

  return (
    <View style={styles.container}>
      <View style={styles.errorContainer}>
        <Ionicons name={content.icon} size={48} color="#ef4444" />
        <Text style={styles.title}>{content.title}</Text>
        <Text style={styles.message}>{content.message}</Text>
        
        <View style={styles.buttonContainer}>
          {content.action && (
            <TouchableOpacity style={styles.retryButton} onPress={content.action}>
              <Ionicons name="refresh" size={20} color="white" />
              <Text style={styles.retryButtonText}>{content.actionText}</Text>
            </TouchableOpacity>
          )}
          
          {onCancel && (
            <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
              <Ionicons name="close" size={20} color="#6b7280" />
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          )}
        </View>
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
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
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
  cancelButton: {
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  cancelButtonText: {
    color: '#6b7280',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default PaymentError; 