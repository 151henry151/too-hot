import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console and any error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You could also log to an error reporting service here
    // Example: Sentry.captureException(error);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleReportError = () => {
    Alert.alert(
      'Report Error',
      'Would you like to report this error to help improve the app?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Report', 
          onPress: () => {
            // Here you could send the error to your backend
            console.log('Error reported:', this.state.error);
            Alert.alert('Thank you', 'Your report has been submitted.');
          }
        }
      ]
    );
  };

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <View style={styles.errorContainer}>
            <Ionicons name="warning-outline" size={64} color="#ef4444" />
            <Text style={styles.title}>Oops! Something went wrong</Text>
            <Text style={styles.message}>
              The app encountered an unexpected error. This helps us improve the app.
            </Text>
            
            <View style={styles.buttonContainer}>
              <TouchableOpacity style={styles.retryButton} onPress={this.handleRetry}>
                <Ionicons name="refresh" size={20} color="white" />
                <Text style={styles.retryButtonText}>Try Again</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.reportButton} onPress={this.handleReportError}>
                <Ionicons name="bug-outline" size={20} color="#6b7280" />
                <Text style={styles.reportButtonText}>Report Error</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

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
    fontSize: 20,
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
    marginBottom: 24,
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
  reportButton: {
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  reportButtonText: {
    color: '#6b7280',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ErrorBoundary; 