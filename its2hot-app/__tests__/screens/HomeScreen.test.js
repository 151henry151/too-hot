import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from '../../screens/HomeScreen';
import { mockWeatherData, mockLocationData } from '../utils/test-utils';

// Mock the services
jest.mock('../../services/UpdateService', () => ({
  checkForUpdates: jest.fn(),
}));

jest.mock('../../services/PaymentService', () => ({
  initializePayment: jest.fn(),
  processPayment: jest.fn(),
}));

// Mock expo-location
jest.mock('expo-location', () => ({
  requestForegroundPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
  getCurrentPositionAsync: jest.fn(() => Promise.resolve({
    coords: { latitude: 40.7128, longitude: -74.0060 }
  })),
}));

// Mock expo-notifications
jest.mock('expo-notifications', () => ({
  requestPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
  getExpoPushTokenAsync: jest.fn(() => Promise.resolve({ data: 'test-token' })),
}));

// Mock expo-haptics
jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  notificationAsync: jest.fn(),
}));

describe('HomeScreen', () => {
  const mockNavigation = {
    navigate: jest.fn(),
    goBack: jest.fn(),
    setOptions: jest.fn(),
  };

  const mockRoute = {
    params: {},
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  describe('Initial Rendering', () => {
    it('renders loading state initially', () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      expect(screen.getByTestId('loading-spinner')).toBeTruthy();
    });

    it('displays app title', () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      expect(screen.getByText('Too Hot Today')).toBeTruthy();
    });

    it('displays temperature when loaded', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('85°F')).toBeTruthy();
      });
    });
  });

  describe('Weather Data Display', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });
    });

    it('displays current temperature', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('85°F')).toBeTruthy();
      });
    });

    it('displays feels like temperature', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Feels like 90°F')).toBeTruthy();
      });
    });

    it('displays humidity', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Humidity: 65%')).toBeTruthy();
      });
    });

    it('displays wind speed', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Wind: 8 mph')).toBeTruthy();
      });
    });

    it('displays weather description', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Partly cloudy')).toBeTruthy();
      });
    });
  });

  describe('Location Handling', () => {
    it('requests location permission on mount', async () => {
      const { requestForegroundPermissionsAsync } = require('expo-location');
      
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(requestForegroundPermissionsAsync).toHaveBeenCalled();
      });
    });

    it('handles location permission denied', async () => {
      const { requestForegroundPermissionsAsync } = require('expo-location');
      requestForegroundPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Location access denied')).toBeTruthy();
      });
    });

    it('displays location error when permission denied', async () => {
      const { requestForegroundPermissionsAsync } = require('expo-location');
      requestForegroundPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Please enable location access to get weather data')).toBeTruthy();
      });
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });
    });

    it('navigates to shop screen when shop button is pressed', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const shopButton = screen.getByText('Shop');
        fireEvent.press(shopButton);
        expect(mockNavigation.navigate).toHaveBeenCalledWith('Shop');
      });
    });

    it('navigates to too hot today screen when button is pressed', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const tooHotButton = screen.getByText('Too Hot Today');
        fireEvent.press(tooHotButton);
        expect(mockNavigation.navigate).toHaveBeenCalledWith('TooHotToday');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error when weather API fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Failed to load weather data')).toBeTruthy();
      });
    });

    it('displays error when weather API returns error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ error: 'Server error' }),
      });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('Failed to load weather data')).toBeTruthy();
      });
    });

    it('provides retry functionality', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const retryButton = screen.getByText('Retry');
        fireEvent.press(retryButton);
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Refresh Functionality', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });
    });

    it('refreshes weather data on pull to refresh', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const refreshControl = screen.getByTestId('refresh-control');
        fireEvent(refreshControl, 'refresh');
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('shows refresh indicator during refresh', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const refreshControl = screen.getByTestId('refresh-control');
        fireEvent(refreshControl, 'refresh');
        expect(screen.getByTestId('refreshing-indicator')).toBeTruthy();
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });
    });

    it('provides accessibility labels for buttons', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const shopButton = screen.getByText('Shop');
        expect(shopButton.props.accessibilityLabel).toBe('Navigate to shop');
        
        const tooHotButton = screen.getByText('Too Hot Today');
        expect(tooHotButton.props.accessibilityLabel).toBe('View too hot today information');
      });
    });

    it('provides accessibility hints for interactive elements', async () => {
      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        const temperatureDisplay = screen.getByText('85°F');
        expect(temperatureDisplay.props.accessibilityHint).toBe('Current temperature');
      });
    });
  });

  describe('Performance', () => {
    it('handles rapid navigation without memory leaks', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockWeatherData),
      });

      const { rerender } = render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      // Simulate rapid navigation
      for (let i = 0; i < 5; i++) {
        rerender(
          <NavigationContainer>
            <HomeScreen navigation={mockNavigation} route={mockRoute} />
          </NavigationContainer>
        );
        await waitFor(() => {
          expect(screen.getByText('85°F')).toBeTruthy();
        });
      }
    });

    it('handles large weather data efficiently', async () => {
      const largeWeatherData = {
        ...mockWeatherData,
        hourly: Array(24).fill().map((_, i) => ({
          dt: Date.now() / 1000 + i * 3600,
          temp: 85 + i,
          weather: [{ description: 'Partly cloudy' }],
        })),
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(largeWeatherData),
      });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('85°F')).toBeTruthy();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles missing weather data gracefully', async () => {
      const incompleteWeatherData = {
        current: {
          temp: 85,
          // Missing other fields
        },
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(incompleteWeatherData),
      });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('85°F')).toBeTruthy();
        // Should not crash when humidity/wind data is missing
      });
    });

    it('handles extreme temperature values', async () => {
      const extremeWeatherData = {
        ...mockWeatherData,
        current: {
          ...mockWeatherData.current,
          temp: -40, // Very cold
          feels_like: 120, // Very hot
        },
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(extremeWeatherData),
      });

      render(
        <NavigationContainer>
          <HomeScreen navigation={mockNavigation} route={mockRoute} />
        </NavigationContainer>
      );

      await waitFor(() => {
        expect(screen.getByText('-40°F')).toBeTruthy();
        expect(screen.getByText('Feels like 120°F')).toBeTruthy();
      });
    });
  });
}); 