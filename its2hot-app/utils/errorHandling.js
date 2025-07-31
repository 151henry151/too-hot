import { Alert } from 'react-native';
import { useLogger } from '../hooks/useLogger';

// Error types and their user-friendly messages
export const ERROR_TYPES = {
  NETWORK_ERROR: 'network_error',
  LOCATION_ERROR: 'location_error',
  PAYMENT_ERROR: 'payment_error',
  NOTIFICATION_ERROR: 'notification_error',
  API_ERROR: 'api_error',
  UNKNOWN_ERROR: 'unknown_error'
};

// Error messages for different scenarios
export const ERROR_MESSAGES = {
  [ERROR_TYPES.NETWORK_ERROR]: {
    title: 'Connection Error',
    message: 'Unable to connect to the server. Please check your internet connection and try again.',
    action: 'Try Again'
  },
  [ERROR_TYPES.LOCATION_ERROR]: {
    title: 'Location Error',
    message: 'Unable to get your location. Please check your location settings and try again.',
    action: 'Open Settings'
  },
  [ERROR_TYPES.PAYMENT_ERROR]: {
    title: 'Payment Error',
    message: 'Unable to process your payment. Please try again or use a different payment method.',
    action: 'Try Again'
  },
  [ERROR_TYPES.NOTIFICATION_ERROR]: {
    title: 'Notification Error',
    message: 'Unable to set up notifications. Please check your notification settings.',
    action: 'Open Settings'
  },
  [ERROR_TYPES.API_ERROR]: {
    title: 'Service Error',
    message: 'Unable to load data. Please try again in a moment.',
    action: 'Try Again'
  },
  [ERROR_TYPES.UNKNOWN_ERROR]: {
    title: 'Something went wrong',
    message: 'An unexpected error occurred. Please try again.',
    action: 'Try Again'
  }
};

// Error handling utility class
export class ErrorHandler {
  constructor() {
    this.logger = useLogger();
  }

  // Handle different types of errors
  handleError(error, type = ERROR_TYPES.UNKNOWN_ERROR, context = '') {
    // Log the error
    this.logger.error(`Error in ${context}: ${error?.message || error}`, 'ErrorHandler', {
      type,
      error: error?.toString(),
      stack: error?.stack
    });

    // Get user-friendly message
    const errorInfo = ERROR_MESSAGES[type] || ERROR_MESSAGES[ERROR_TYPES.UNKNOWN_ERROR];

    // Show alert to user
    Alert.alert(
      errorInfo.title,
      errorInfo.message,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: errorInfo.action, onPress: () => this.handleRetry(error, type, context) }
      ]
    );
  }

  // Handle retry logic
  handleRetry(error, type, context) {
    this.logger.info(`User retrying after ${type} error in ${context}`, 'ErrorHandler');
    
    // You can implement specific retry logic here
    // For example, retry API calls, location requests, etc.
    switch (type) {
      case ERROR_TYPES.NETWORK_ERROR:
        // Retry network request
        break;
      case ERROR_TYPES.LOCATION_ERROR:
        // Retry location request
        break;
      case ERROR_TYPES.PAYMENT_ERROR:
        // Retry payment
        break;
      default:
        // Generic retry
        break;
    }
  }

  // Handle network errors specifically
  handleNetworkError(error, context = '') {
    this.handleError(error, ERROR_TYPES.NETWORK_ERROR, context);
  }

  // Handle location errors specifically
  handleLocationError(error, context = '') {
    this.handleError(error, ERROR_TYPES.LOCATION_ERROR, context);
  }

  // Handle payment errors specifically
  handlePaymentError(error, context = '') {
    this.handleError(error, ERROR_TYPES.PAYMENT_ERROR, context);
  }

  // Handle API errors specifically
  handleApiError(error, context = '') {
    this.handleError(error, ERROR_TYPES.API_ERROR, context);
  }

  // Handle notification errors specifically
  handleNotificationError(error, context = '') {
    this.handleError(error, ERROR_TYPES.NOTIFICATION_ERROR, context);
  }

  // Check if error is a network error
  isNetworkError(error) {
    return (
      error?.message?.includes('Network') ||
      error?.message?.includes('fetch') ||
      error?.message?.includes('timeout') ||
      error?.code === 'NETWORK_ERROR'
    );
  }

  // Check if error is a location error
  isLocationError(error) {
    return (
      error?.message?.includes('Location') ||
      error?.message?.includes('permission') ||
      error?.code === 'LOCATION_ERROR'
    );
  }

  // Check if error is a payment error
  isPaymentError(error) {
    return (
      error?.message?.includes('Payment') ||
      error?.message?.includes('card') ||
      error?.message?.includes('declined') ||
      error?.code === 'PAYMENT_ERROR'
    );
  }

  // Auto-detect error type and handle appropriately
  handleErrorAuto(error, context = '') {
    if (this.isNetworkError(error)) {
      this.handleNetworkError(error, context);
    } else if (this.isLocationError(error)) {
      this.handleLocationError(error, context);
    } else if (this.isPaymentError(error)) {
      this.handlePaymentError(error, context);
    } else {
      this.handleError(error, ERROR_TYPES.UNKNOWN_ERROR, context);
    }
  }
}

// Create singleton instance
export const errorHandler = new ErrorHandler();

// Hook for using error handling in components
export const useErrorHandling = () => {
  return {
    handleError: errorHandler.handleError.bind(errorHandler),
    handleNetworkError: errorHandler.handleNetworkError.bind(errorHandler),
    handleLocationError: errorHandler.handleLocationError.bind(errorHandler),
    handlePaymentError: errorHandler.handlePaymentError.bind(errorHandler),
    handleApiError: errorHandler.handleApiError.bind(errorHandler),
    handleNotificationError: errorHandler.handleNotificationError.bind(errorHandler),
    handleErrorAuto: errorHandler.handleErrorAuto.bind(errorHandler),
    isNetworkError: errorHandler.isNetworkError.bind(errorHandler),
    isLocationError: errorHandler.isLocationError.bind(errorHandler),
    isPaymentError: errorHandler.isPaymentError.bind(errorHandler),
    ERROR_TYPES,
    ERROR_MESSAGES
  };
};

export default errorHandler; 