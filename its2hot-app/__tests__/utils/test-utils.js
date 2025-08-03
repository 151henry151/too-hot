import React from 'react';
import { render } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';

// Custom render function that includes navigation context
export const renderWithNavigation = (component, options = {}) => {
  return render(
    <NavigationContainer>
      {component}
    </NavigationContainer>,
    options
  );
};

// Mock data for testing
export const mockWeatherData = {
  current: {
    temp: 85,
    feels_like: 90,
    humidity: 65,
    wind_speed: 8,
    weather: [{ description: 'Partly cloudy' }],
  },
  daily: [
    {
      dt: Date.now() / 1000,
      temp: { day: 85, min: 70, max: 90 },
      weather: [{ description: 'Partly cloudy' }],
    },
  ],
};

export const mockLocationData = {
  latitude: 40.7128,
  longitude: -74.0060,
  city: 'New York',
  state: 'NY',
  country: 'US',
};

export const mockProductData = {
  id: 'test-product-1',
  name: 'Test T-Shirt',
  price: 29.99,
  description: 'A test t-shirt for testing',
  images: ['test-image-1.jpg', 'test-image-2.jpg'],
  variants: [
    { id: 'variant-1', name: 'Small', color: 'Black' },
    { id: 'variant-2', name: 'Medium', color: 'White' },
  ],
};

export const mockUserData = {
  id: 'test-user-1',
  email: 'test@example.com',
  name: 'Test User',
  preferences: {
    notifications: true,
    location: true,
  },
};

// Mock functions
export const mockFetch = (response, status = 200) => {
  return Promise.resolve({
    ok: status < 400,
    status,
    json: () => Promise.resolve(response),
    text: () => Promise.resolve(JSON.stringify(response)),
  });
};

export const mockAsyncStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Test constants
export const TEST_IDS = {
  LOADING_SPINNER: 'loading-spinner',
  ERROR_MESSAGE: 'error-message',
  SUCCESS_MESSAGE: 'success-message',
  BUTTON_PRIMARY: 'button-primary',
  BUTTON_SECONDARY: 'button-secondary',
  INPUT_FIELD: 'input-field',
  CARD_CONTAINER: 'card-container',
  LIST_ITEM: 'list-item',
  MODAL_CONTAINER: 'modal-container',
  TAB_BAR: 'tab-bar',
  NAVIGATION_HEADER: 'navigation-header',
};

// Custom matchers for common assertions
export const expectElementToBeVisible = (element) => {
  expect(element).toBeTruthy();
  expect(element.props.style).not.toEqual(
    expect.objectContaining({ display: 'none' })
  );
};

export const expectElementToBeDisabled = (element) => {
  expect(element.props.disabled).toBe(true);
  expect(element.props.accessibilityState?.disabled).toBe(true);
};

export const expectElementToBeEnabled = (element) => {
  expect(element.props.disabled).toBe(false);
  expect(element.props.accessibilityState?.disabled).toBe(false);
};

// Helper to wait for async operations
export const waitForAsync = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms));

// Helper to create mock navigation props
export const createMockNavigationProps = (params = {}) => ({
  navigation: {
    navigate: jest.fn(),
    goBack: jest.fn(),
    setOptions: jest.fn(),
    addListener: jest.fn(),
    remove: jest.fn(),
  },
  route: {
    params,
    name: 'TestScreen',
  },
});

// Helper to create mock route params
export const createMockRouteParams = (params = {}) => ({
  ...params,
});

// Test data factories
export const createMockWeatherData = (overrides = {}) => ({
  ...mockWeatherData,
  ...overrides,
});

export const createMockProductData = (overrides = {}) => ({
  ...mockProductData,
  ...overrides,
});

export const createMockUserData = (overrides = {}) => ({
  ...mockUserData,
  ...overrides,
});

// Accessibility helpers
export const expectToBeAccessible = (element) => {
  expect(element.props.accessibilityLabel).toBeDefined();
  expect(element.props.accessibilityRole).toBeDefined();
};

export const expectToHaveAccessibilityHint = (element) => {
  expect(element.props.accessibilityHint).toBeDefined();
};

// Performance helpers
export const measurePerformance = async (callback) => {
  const start = performance.now();
  await callback();
  const end = performance.now();
  return end - start;
};

// Network helpers
export const mockNetworkError = () => {
  global.fetch.mockRejectedValueOnce(new Error('Network error'));
};

export const mockNetworkSuccess = (data) => {
  global.fetch.mockResolvedValueOnce(mockFetch(data));
};

// Storage helpers
export const mockStorageGet = (key, value) => {
  mockAsyncStorage.getItem.mockResolvedValueOnce(JSON.stringify(value));
};

export const mockStorageSet = (key, value) => {
  mockAsyncStorage.setItem.mockResolvedValueOnce();
};

// Location helpers
export const mockLocationPermission = (status = 'granted') => {
  const { requestForegroundPermissionsAsync } = require('expo-location');
  requestForegroundPermissionsAsync.mockResolvedValueOnce({ status });
};

export const mockLocationCoords = (coords = { latitude: 40.7128, longitude: -74.0060 }) => {
  const { getCurrentPositionAsync } = require('expo-location');
  getCurrentPositionAsync.mockResolvedValueOnce({ coords });
};

// Notification helpers
export const mockNotificationPermission = (status = 'granted') => {
  const { requestPermissionsAsync } = require('expo-notifications');
  requestPermissionsAsync.mockResolvedValueOnce({ status });
};

// Payment helpers
export const mockStripeSuccess = () => {
  const { useStripe } = require('@stripe/stripe-react-native');
  const mockStripe = {
    initPaymentSheet: jest.fn(() => Promise.resolve({ error: null })),
    presentPaymentSheet: jest.fn(() => Promise.resolve({ error: null })),
    createPaymentMethod: jest.fn(() => Promise.resolve({ error: null })),
  };
  useStripe.mockReturnValue(mockStripe);
  return mockStripe;
};

export const mockStripeError = (error = 'Payment failed') => {
  const { useStripe } = require('@stripe/stripe-react-native');
  const mockStripe = {
    initPaymentSheet: jest.fn(() => Promise.resolve({ error })),
    presentPaymentSheet: jest.fn(() => Promise.resolve({ error })),
    createPaymentMethod: jest.fn(() => Promise.resolve({ error })),
  };
  useStripe.mockReturnValue(mockStripe);
  return mockStripe;
}; 