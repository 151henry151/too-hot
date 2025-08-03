# Loading States Implementation Guide

## Overview

This document outlines the comprehensive loading state system implemented for the Too Hot app, ensuring app store compliance and excellent user experience.

## Components

### 1. LoadingState Component

A flexible loading component with multiple types and configurations:

```javascript
import LoadingState from '../components/LoadingState';

// Basic usage
<LoadingState message="Loading..." />

// With progress
<LoadingState 
  message="Downloading update..." 
  showProgress={true}
  progress={75}
/>

// Overlay type
<LoadingState 
  type="overlay"
  message="Processing payment..."
  onRetry={() => handleRetry()}
/>

// Compact type for buttons
<LoadingState 
  type="compact"
  message="Subscribing..."
/>
```

#### Props
- `message`: Loading message text
- `type`: Loading type (`default`, `compact`, `overlay`, `skeleton`)
- `showProgress`: Show progress bar
- `progress`: Progress value (0-100)
- `onRetry`: Retry callback function
- `retryText`: Custom retry button text
- `color`: Custom color for spinner and text
- `size`: Spinner size (`small`, `large`)
- `showIcon`: Show/hide icon
- `iconName`: Custom icon name

### 2. LoadingWrapper Components

#### LoadingWrapper
Wraps content and shows loading state when needed:

```javascript
import LoadingWrapper from '../components/LoadingWrapper';

<LoadingWrapper
  loadingKey={LOADING_KEYS.LOCATION_FETCH}
  loadingMessage="Getting your location..."
>
  <YourComponent />
</LoadingWrapper>
```

#### LoadingOverlay
Shows loading overlay on top of content:

```javascript
import { LoadingOverlay } from '../components/LoadingWrapper';

<LoadingOverlay
  loadingKey={LOADING_KEYS.PAYMENT_PROCESS}
  loadingMessage="Processing payment..."
>
  <PaymentForm />
</LoadingOverlay>
```

#### LoadingButton
Shows loading state in buttons:

```javascript
import { LoadingButton } from '../components/LoadingWrapper';

<LoadingButton
  loadingKey={LOADING_KEYS.NOTIFICATION_SUBSCRIBE}
  onPress={handleSubscribe}
>
  <TouchableOpacity style={styles.button}>
    <Text>Subscribe</Text>
  </TouchableOpacity>
</LoadingButton>
```

#### LoadingSkeleton
Shows skeleton loading states:

```javascript
import { LoadingSkeleton } from '../components/LoadingWrapper';

<LoadingSkeleton
  loadingKey={LOADING_KEYS.DATA_LOAD}
  skeletonCount={3}
>
  <DataList />
</LoadingSkeleton>
```

## Hook: useLoadingState

Comprehensive loading state management hook:

```javascript
import { useLoadingState, LOADING_KEYS, LOADING_MESSAGES } from '../hooks/useLoadingState';

const { 
  setLoading, 
  withLoading, 
  withProgress, 
  isLoading, 
  getLoadingMessage 
} = useLoadingState();

// Set loading state
setLoading(LOADING_KEYS.LOCATION_FETCH, true, 'Getting location...');

// Execute with loading
const result = await withLoading(LOADING_KEYS.API_CALL, async () => {
  return await fetchData();
}, 'Loading data...');

// Execute with progress
const result = await withProgress(LOADING_KEYS.UPDATE_DOWNLOAD, async (progress) => {
  // Update progress during operation
  progress(50);
  return await downloadUpdate();
}, 'Downloading update...');
```

## Predefined Loading Keys

### App Initialization
- `APP_INIT`: App initialization
- `SPLASH_SCREEN`: Splash screen loading

### Location Services
- `LOCATION_PERMISSION`: Location permission request
- `LOCATION_FETCH`: Getting current location
- `LOCATION_GEOCODE`: Reverse geocoding

### Notifications
- `NOTIFICATION_PERMISSION`: Notification permission request
- `NOTIFICATION_SUBSCRIBE`: Subscribing to notifications
- `NOTIFICATION_UNSUBSCRIBE`: Unsubscribing from notifications

### Network Operations
- `API_CALL`: Generic API calls
- `WEATHER_FETCH`: Fetching weather data
- `DEVICE_REGISTRATION`: Registering device with backend

### Payment Processing
- `PAYMENT_INIT`: Payment initialization
- `PAYMENT_PROCESS`: Payment processing
- `PAYMENT_CONFIRM`: Payment confirmation

### App Updates
- `UPDATE_CHECK`: Checking for updates
- `UPDATE_DOWNLOAD`: Downloading updates
- `UPDATE_APPLY`: Applying updates

### Navigation
- `NAVIGATION`: Navigation operations
- `SCREEN_LOAD`: Screen loading

### Data Operations
- `DATA_LOAD`: Loading data
- `DATA_SAVE`: Saving data
- `DATA_SYNC`: Syncing data

## Implementation Examples

### 1. Location Services

```javascript
const getUserLocation = async () => {
  return await withLoading(LOADING_KEYS.LOCATION_FETCH, async () => {
    // Request permission
    setLoading(LOADING_KEYS.LOCATION_PERMISSION, true);
    const { status } = await Location.requestForegroundPermissionsAsync();
    setLoading(LOADING_KEYS.LOCATION_PERMISSION, false);
    
    if (status !== 'granted') {
      throw new Error('Location permission denied');
    }
    
    // Get location
    const location = await Location.getCurrentPositionAsync();
    
    // Geocode
    setLoading(LOADING_KEYS.LOCATION_GEOCODE, true);
    const geocode = await Location.reverseGeocodeAsync(location.coords);
    setLoading(LOADING_KEYS.LOCATION_GEOCODE, false);
    
    return geocode[0];
  }, LOADING_MESSAGES[LOADING_KEYS.LOCATION_FETCH]);
};
```

### 2. Payment Processing

```javascript
const processPayment = async (orderData) => {
  return await withProgress(LOADING_KEYS.PAYMENT_PROCESS, async (progress) => {
    // Initialize payment
    progress(25);
    await PaymentService.initializePayment(orderData);
    
    // Process payment
    progress(50);
    const result = await PaymentService.processPayment();
    
    // Confirm payment
    progress(75);
    await PaymentService.confirmPayment(result);
    
    progress(100);
    return result;
  }, LOADING_MESSAGES[LOADING_KEYS.PAYMENT_PROCESS]);
};
```

### 3. App Updates

```javascript
const checkForUpdates = async () => {
  return await withLoading(LOADING_KEYS.UPDATE_CHECK, async () => {
    const update = await Updates.checkForUpdateAsync();
    
    if (update.isAvailable) {
      return await withProgress(LOADING_KEYS.UPDATE_DOWNLOAD, async (progress) => {
        const result = await Updates.fetchUpdateAsync();
        progress(100);
        return result;
      }, LOADING_MESSAGES[LOADING_KEYS.UPDATE_DOWNLOAD]);
    }
    
    return null;
  }, LOADING_MESSAGES[LOADING_KEYS.UPDATE_CHECK]);
};
```

## UI Integration

### 1. Screen Loading

```javascript
// Wrap entire screen with loading overlay
<LoadingOverlay
  loadingKey={LOADING_KEYS.SCREEN_LOAD}
  loadingMessage="Loading screen..."
>
  <YourScreen />
</LoadingOverlay>
```

### 2. Button Loading

```javascript
// Wrap buttons with loading state
<LoadingButton
  loadingKey={LOADING_KEYS.NOTIFICATION_SUBSCRIBE}
  onPress={handleSubscribe}
>
  <TouchableOpacity style={styles.button}>
    <Text>Subscribe to Alerts</Text>
  </TouchableOpacity>
</LoadingButton>
```

### 3. Content Loading

```javascript
// Wrap content with loading wrapper
<LoadingWrapper
  loadingKey={LOADING_KEYS.DATA_LOAD}
  loadingType="skeleton"
>
  <DataList />
</LoadingWrapper>
```

## Best Practices

### 1. Loading State Management
- Use predefined loading keys for consistency
- Set appropriate loading messages
- Clear loading states when operations complete
- Handle errors gracefully

### 2. User Experience
- Show loading states for operations > 100ms
- Use progress indicators for long operations
- Provide retry options for failed operations
- Use appropriate loading types for context

### 3. Performance
- Avoid unnecessary loading states
- Clear loading states promptly
- Use skeleton loading for content
- Implement proper error handling

### 4. Accessibility
- Provide meaningful loading messages
- Support screen readers
- Use appropriate ARIA labels
- Maintain keyboard navigation

## App Store Compliance

### 1. Loading States
- ✅ Comprehensive loading states implemented
- ✅ Progress indicators for long operations
- ✅ Retry mechanisms for failed operations
- ✅ Appropriate loading messages

### 2. User Experience
- ✅ No blank screens during loading
- ✅ Clear feedback for user actions
- ✅ Graceful error handling
- ✅ Consistent loading patterns

### 3. Performance
- ✅ Efficient loading state management
- ✅ Minimal loading overhead
- ✅ Proper state cleanup
- ✅ Optimized loading components

## Testing

### 1. Loading State Tests
```javascript
describe('Loading States', () => {
  it('shows loading state during API calls', async () => {
    const { getByText } = render(<HomeScreen />);
    
    fireEvent.press(getByText('Subscribe to Alerts'));
    
    expect(getByText('Subscribing to alerts...')).toBeTruthy();
  });
  
  it('shows progress for long operations', async () => {
    const { getByText } = render(<UpdateScreen />);
    
    fireEvent.press(getByText('Check for Updates'));
    
    expect(getByText('Downloading update...')).toBeTruthy();
  });
});
```

### 2. Error Handling Tests
```javascript
describe('Error Handling', () => {
  it('shows retry option for failed operations', async () => {
    // Mock failed API call
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    
    const { getByText } = render(<HomeScreen />);
    
    fireEvent.press(getByText('Subscribe to Alerts'));
    
    expect(getByText('Retry')).toBeTruthy();
  });
});
```

## Future Enhancements

### 1. Advanced Loading States
- Skeleton loading for complex content
- Progressive loading for images
- Lazy loading for large lists
- Background loading indicators

### 2. Performance Optimizations
- Loading state caching
- Preloading strategies
- Optimistic updates
- Background sync indicators

### 3. Accessibility Improvements
- Voice feedback for loading states
- Custom loading animations
- High contrast loading indicators
- Reduced motion support

## Conclusion

The loading state system provides a comprehensive solution for managing loading states throughout the app, ensuring excellent user experience and app store compliance. The system is flexible, performant, and follows best practices for React Native development.

Key benefits:
- ✅ Consistent loading experience
- ✅ App store compliance
- ✅ Excellent user experience
- ✅ Comprehensive error handling
- ✅ Accessibility support
- ✅ Performance optimized 