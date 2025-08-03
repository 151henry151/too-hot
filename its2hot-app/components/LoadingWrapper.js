import React from 'react';
import { View, StyleSheet } from 'react-native';
import LoadingState from './LoadingState';
import { useLoadingState } from '../hooks/useLoadingState';

/**
 * LoadingWrapper component that wraps content and shows loading states
 * Supports multiple loading states and progress tracking
 */
const LoadingWrapper = ({
  children,
  loadingKey,
  loadingMessage,
  loadingType = 'default',
  showProgress = false,
  progressKey,
  onRetry,
  retryText,
  containerStyle,
  loadingContainerStyle,
  fallback = null,
  disabled = false
}) => {
  const { isLoading, getLoadingMessage, getProgress } = useLoadingState();
  
  // If disabled, just render children
  if (disabled) {
    return children;
  }

  // Check if this specific loading state is active
  const isCurrentlyLoading = isLoading(loadingKey);
  const currentMessage = loadingMessage || getLoadingMessage(loadingKey);
  const currentProgress = showProgress && progressKey ? getProgress(progressKey) : undefined;

  // If loading, show loading state
  if (isCurrentlyLoading) {
    return (
      <View style={[styles.container, containerStyle]}>
        <LoadingState
          message={currentMessage}
          type={loadingType}
          progress={currentProgress}
          showProgress={showProgress}
          onRetry={onRetry}
          retryText={retryText}
          containerStyle={loadingContainerStyle}
        />
      </View>
    );
  }

  // If not loading, render children or fallback
  return children || fallback;
};

/**
 * LoadingOverlay component that shows loading overlay on top of content
 */
const LoadingOverlay = ({
  children,
  loadingKey,
  loadingMessage,
  showProgress = false,
  progressKey,
  onRetry,
  retryText,
  containerStyle
}) => {
  const { isLoading, getLoadingMessage, getProgress } = useLoadingState();
  
  const isCurrentlyLoading = isLoading(loadingKey);
  const currentMessage = loadingMessage || getLoadingMessage(loadingKey);
  const currentProgress = showProgress && progressKey ? getProgress(progressKey) : undefined;

  return (
    <View style={[styles.overlayContainer, containerStyle]}>
      {children}
      {isCurrentlyLoading && (
        <LoadingState
          message={currentMessage}
          type="overlay"
          progress={currentProgress}
          showProgress={showProgress}
          onRetry={onRetry}
          retryText={retryText}
        />
      )}
    </View>
  );
};

/**
 * LoadingButton component that shows loading state in a button
 */
const LoadingButton = ({
  children,
  loadingKey,
  loadingMessage,
  onPress,
  disabled,
  style,
  textStyle,
  ...buttonProps
}) => {
  const { isLoading, getLoadingMessage } = useLoadingState();
  
  const isCurrentlyLoading = isLoading(loadingKey);
  const currentMessage = loadingMessage || getLoadingMessage(loadingKey);

  return (
    <View style={[styles.buttonContainer, style]}>
      {isCurrentlyLoading ? (
        <LoadingState
          message={currentMessage}
          type="compact"
          containerStyle={styles.buttonLoading}
        />
      ) : (
        React.cloneElement(children, {
          onPress: isCurrentlyLoading ? undefined : onPress,
          disabled: disabled || isCurrentlyLoading,
          style: [children.props.style, textStyle],
          ...buttonProps
        })
      )}
    </View>
  );
};

/**
 * LoadingSkeleton component for showing skeleton loading states
 */
const LoadingSkeleton = ({
  children,
  loadingKey,
  skeletonCount = 3,
  containerStyle
}) => {
  const { isLoading } = useLoadingState();
  
  const isCurrentlyLoading = isLoading(loadingKey);

  if (isCurrentlyLoading) {
    return (
      <View style={[styles.skeletonContainer, containerStyle]}>
        {Array.from({ length: skeletonCount }).map((_, index) => (
          <LoadingState
            key={index}
            type="skeleton"
            containerStyle={styles.skeletonItem}
          />
        ))}
      </View>
    );
  }

  return children;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  overlayContainer: {
    flex: 1,
    position: 'relative',
  },
  buttonContainer: {
    minHeight: 44,
    justifyContent: 'center',
  },
  buttonLoading: {
    padding: 8,
  },
  skeletonContainer: {
    flex: 1,
  },
  skeletonItem: {
    marginBottom: 8,
  },
});

export { LoadingWrapper, LoadingOverlay, LoadingButton, LoadingSkeleton };
export default LoadingWrapper; 