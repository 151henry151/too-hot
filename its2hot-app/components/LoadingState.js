import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useColorScheme } from 'react-native';

const { width } = Dimensions.get('window');

const LoadingState = ({ 
  message = "Loading...", 
  showIcon = true,
  size = "large",
  color,
  type = "default", // default, compact, overlay, skeleton
  progress, // 0-100 for progress indicator
  showProgress = false,
  iconName = "thermometer-outline",
  backgroundColor,
  textColor,
  containerStyle,
  onRetry,
  retryText = "Retry"
}) => {
  const colorScheme = useColorScheme();
  
  // Default colors based on theme
  const defaultColor = color || (colorScheme === 'dark' ? '#60a5fa' : '#3b82f6');
  const defaultBgColor = backgroundColor || (colorScheme === 'dark' ? '#1f2937' : '#f9fafb');
  const defaultTextColor = textColor || (colorScheme === 'dark' ? '#d1d5db' : '#6b7280');

  const renderIcon = () => {
    if (!showIcon) return null;
    
    const iconSize = type === 'compact' ? 24 : 48;
    return (
      <Ionicons 
        name={iconName} 
        size={iconSize} 
        color={defaultColor} 
        style={[styles.icon, type === 'compact' && styles.compactIcon]} 
      />
    );
  };

  const renderProgress = () => {
    if (!showProgress || progress === undefined) return null;
    
    return (
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { width: `${progress}%`, backgroundColor: defaultColor }
            ]} 
          />
        </View>
        <Text style={[styles.progressText, { color: defaultTextColor }]}>
          {Math.round(progress)}%
        </Text>
      </View>
    );
  };

  const renderRetryButton = () => {
    if (!onRetry) return null;
    
    return (
      <View style={styles.retryContainer}>
        <Text style={[styles.retryText, { color: defaultColor }]}>
          {retryText}
        </Text>
      </View>
    );
  };

  if (type === 'overlay') {
    return (
      <View style={[styles.overlayContainer, { backgroundColor: 'rgba(0,0,0,0.5)' }]}>
        <View style={[styles.overlayContent, { backgroundColor: defaultBgColor }]}>
          {renderIcon()}
          <ActivityIndicator size={size} color={defaultColor} style={styles.spinner} />
          <Text style={[styles.message, { color: defaultTextColor }]}>{message}</Text>
          {renderProgress()}
          {renderRetryButton()}
        </View>
      </View>
    );
  }

  if (type === 'compact') {
    return (
      <View style={[styles.compactContainer, containerStyle]}>
        <ActivityIndicator size="small" color={defaultColor} />
        <Text style={[styles.compactMessage, { color: defaultTextColor }]}>{message}</Text>
      </View>
    );
  }

  if (type === 'skeleton') {
    return (
      <View style={[styles.skeletonContainer, containerStyle]}>
        <View style={[styles.skeletonItem, { backgroundColor: defaultBgColor }]} />
        <View style={[styles.skeletonItem, { backgroundColor: defaultBgColor, width: '70%' }]} />
        <View style={[styles.skeletonItem, { backgroundColor: defaultBgColor, width: '50%' }]} />
      </View>
    );
  }

  // Default loading state
  return (
    <View style={[styles.container, { backgroundColor: defaultBgColor }, containerStyle]}>
      <View style={[styles.loadingContainer, { backgroundColor: colorScheme === 'dark' ? '#374151' : 'white' }]}>
        {renderIcon()}
        <ActivityIndicator size={size} color={defaultColor} style={styles.spinner} />
        <Text style={[styles.message, { color: defaultTextColor }]}>{message}</Text>
        {renderProgress()}
        {renderRetryButton()}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingContainer: {
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
    minWidth: 200,
  },
  icon: {
    marginBottom: 16,
  },
  compactIcon: {
    marginBottom: 8,
  },
  spinner: {
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '500',
  },
  progressContainer: {
    width: '100%',
    marginTop: 12,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e5e7eb',
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 12,
    textAlign: 'center',
    fontWeight: '500',
  },
  retryContainer: {
    marginTop: 12,
    padding: 8,
  },
  retryText: {
    fontSize: 14,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  overlayContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  overlayContent: {
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    maxWidth: 250,
    minWidth: 250,
  },
  compactContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
  compactMessage: {
    fontSize: 14,
    marginLeft: 8,
  },
  skeletonContainer: {
    padding: 16,
  },
  skeletonItem: {
    height: 16,
    borderRadius: 4,
    marginBottom: 8,
    opacity: 0.6,
  },
});

export default LoadingState; 