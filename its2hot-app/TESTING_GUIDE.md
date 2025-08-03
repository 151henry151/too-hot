# Testing Guide for Too Hot App

## Overview

This document provides a comprehensive guide for testing the Too Hot Expo app, including setup, best practices, and coverage requirements.

## Test Structure

```
__tests__/
├── components/          # Component tests
├── hooks/              # Custom hook tests
├── screens/            # Screen component tests
├── services/           # Service layer tests
├── utils/              # Test utilities and helpers
└── setup.js           # Global test setup
```

## Test Coverage Requirements

### Industry Standards
- **Statements**: 80%
- **Branches**: 80%
- **Functions**: 80%
- **Lines**: 80%

### Current Coverage Status
- **useLogger hook**: 75% (Good foundation)
- **Components**: 0% (Needs implementation)
- **Screens**: 0% (Needs implementation)
- **Services**: 0% (Needs implementation)

## Test Categories

### 1. Unit Tests
- **Components**: Test individual React components
- **Hooks**: Test custom React hooks
- **Services**: Test business logic and API calls
- **Utils**: Test utility functions

### 2. Integration Tests
- **Screen Navigation**: Test navigation between screens
- **Data Flow**: Test data passing between components
- **API Integration**: Test service layer integration

### 3. Accessibility Tests
- **Screen Reader Support**: Test accessibility labels and hints
- **Keyboard Navigation**: Test keyboard accessibility
- **Color Contrast**: Test visual accessibility

### 4. Performance Tests
- **Render Performance**: Test component rendering speed
- **Memory Usage**: Test for memory leaks
- **Network Performance**: Test API call efficiency

## Test Setup

### Dependencies
```json
{
  "@testing-library/react-native": "^12.4.3",
  "@testing-library/jest-native": "^5.4.3",
  "jest": "^29.7.0",
  "jest-expo": "~53.0.0",
  "react-test-renderer": "19.0.0",
  "@types/jest": "^29.5.0"
}
```

### Configuration
```json
{
  "jest": {
    "preset": "jest-expo",
    "setupFilesAfterEnv": ["<rootDir>/__tests__/setup.js"],
    "collectCoverageFrom": [
      "**/*.{js,jsx,ts,tsx}",
      "!**/node_modules/**",
      "!**/coverage/**"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## Mock Strategy

### Expo Modules
```javascript
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
```

### React Navigation
```javascript
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    setOptions: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
  }),
}));
```

### Stripe
```javascript
jest.mock('@stripe/stripe-react-native', () => ({
  StripeProvider: ({ children }) => children,
  useStripe: () => ({
    initPaymentSheet: jest.fn(() => Promise.resolve({ error: null })),
    presentPaymentSheet: jest.fn(() => Promise.resolve({ error: null })),
  }),
}));
```

## Test Utilities

### Custom Render Function
```javascript
export const renderWithNavigation = (component, options = {}) => {
  return render(
    <NavigationContainer>
      {component}
    </NavigationContainer>,
    options
  );
};
```

### Mock Data
```javascript
export const mockWeatherData = {
  current: {
    temp: 85,
    feels_like: 90,
    humidity: 65,
    wind_speed: 8,
    weather: [{ description: 'Partly cloudy' }],
  },
};
```

### Test Helpers
```javascript
export const waitForAsync = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms));

export const expectToBeAccessible = (element) => {
  expect(element.props.accessibilityLabel).toBeDefined();
  expect(element.props.accessibilityRole).toBeDefined();
};
```

## Test Patterns

### Component Testing
```javascript
describe('ComponentName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<ComponentName />);
    expect(screen.getByText('Expected Text')).toBeTruthy();
  });

  it('handles user interactions', () => {
    render(<ComponentName />);
    fireEvent.press(screen.getByText('Button'));
    expect(mockFunction).toHaveBeenCalled();
  });

  it('is accessible', () => {
    render(<ComponentName />);
    const element = screen.getByText('Text');
    expectToBeAccessible(element);
  });
});
```

### Hook Testing
```javascript
describe('useCustomHook', () => {
  it('returns expected values', () => {
    const { result } = renderHook(() => useCustomHook());
    expect(result.current.value).toBe(expectedValue);
  });

  it('handles state changes', async () => {
    const { result } = renderHook(() => useCustomHook());
    await act(async () => {
      await result.current.updateValue('new value');
    });
    expect(result.current.value).toBe('new value');
  });
});
```

### Service Testing
```javascript
describe('ServiceName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('handles successful API calls', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await ServiceName.method();
    expect(result.success).toBe(true);
  });

  it('handles API errors', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const result = await ServiceName.method();
    expect(result.success).toBe(false);
    expect(result.error).toContain('Network error');
  });
});
```

## Running Tests

### Commands
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=ComponentName.test.js

# Run tests with verbose output
npm test -- --verbose
```

### Coverage Reports
```bash
# Generate HTML coverage report
npm run test:coverage:html

# Generate coverage for CI
npm run test:ci
```

## Best Practices

### 1. Test Organization
- Group related tests using `describe` blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Mocking Strategy
- Mock external dependencies
- Use realistic mock data
- Test error scenarios

### 3. Accessibility Testing
- Test screen reader support
- Verify keyboard navigation
- Check color contrast compliance

### 4. Performance Testing
- Test render performance
- Monitor memory usage
- Test network efficiency

### 5. Error Handling
- Test error boundaries
- Verify error messages
- Test recovery scenarios

## Common Issues and Solutions

### 1. Mock Setup Issues
**Problem**: Tests fail due to missing mocks
**Solution**: Add comprehensive mocks in `setup.js`

### 2. Async Testing
**Problem**: Async operations not properly tested
**Solution**: Use `act()` and `waitFor()`

### 3. Navigation Testing
**Problem**: Navigation context missing
**Solution**: Use `renderWithNavigation` utility

### 4. Coverage Gaps
**Problem**: Low coverage in certain areas
**Solution**: Add specific tests for uncovered code paths

## Future Improvements

### 1. E2E Testing
- Add Detox for end-to-end testing
- Test complete user workflows
- Test on real devices

### 2. Visual Testing
- Add screenshot testing
- Test UI consistency
- Test responsive design

### 3. Performance Testing
- Add performance benchmarks
- Test memory usage
- Test network efficiency

### 4. Security Testing
- Test input validation
- Test authentication flows
- Test data protection

## Coverage Goals

### Phase 1 (Current)
- [x] Setup test infrastructure
- [x] Implement useLogger tests
- [ ] Implement component tests
- [ ] Implement service tests

### Phase 2 (Next)
- [ ] Implement screen tests
- [ ] Add integration tests
- [ ] Add accessibility tests
- [ ] Achieve 80% coverage

### Phase 3 (Future)
- [ ] Add E2E tests
- [ ] Add performance tests
- [ ] Add visual regression tests
- [ ] Maintain 90%+ coverage

## Resources

- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Expo Testing Guide](https://docs.expo.dev/guides/testing/)
- [Accessibility Testing](https://www.w3.org/WAI/WCAG21/quickref/)

## Contributing

When adding new tests:
1. Follow the established patterns
2. Ensure proper mocking
3. Test edge cases
4. Maintain coverage requirements
5. Update this documentation 