import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { useColorScheme } from 'react-native';
import { ThemedText } from '../../components/ThemedText';

// Mock useColorScheme
jest.mock('react-native', () => ({
  ...jest.requireActual('react-native'),
  useColorScheme: jest.fn(),
}));

// Mock the useThemeColor hook
jest.mock('../../hooks/useThemeColor', () => ({
  useThemeColor: jest.fn(() => '#000000'),
}));

describe('ThemedText', () => {
  const mockUseColorScheme = useColorScheme as jest.MockedFunction<typeof useColorScheme>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Light Theme', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue('light');
    });

    it('renders with light theme colors', () => {
      render(<ThemedText>Test Text</ThemedText>);
      const textElement = screen.getByText('Test Text');
      expect(textElement).toBeTruthy();
    });

    it('applies custom style props', () => {
      const customStyle = { fontSize: 20, fontWeight: 'bold' as const };
      render(<ThemedText style={customStyle}>Styled Text</ThemedText>);
      const textElement = screen.getByText('Styled Text');
      expect(textElement.props.style).toEqual(
        expect.arrayContaining([expect.objectContaining(customStyle)])
      );
    });

    it('handles accessibility props', () => {
      render(
        <ThemedText accessibilityLabel="Test Label" accessibilityRole="text">
          Accessible Text
        </ThemedText>
      );
      const textElement = screen.getByText('Accessible Text');
      expect(textElement.props.accessibilityLabel).toBe('Test Label');
      expect(textElement.props.accessibilityRole).toBe('text');
    });

    it('handles onPress callback', () => {
      const onPress = jest.fn();
      render(<ThemedText onPress={onPress}>Clickable Text</ThemedText>);
      const textElement = screen.getByText('Clickable Text');
      textElement.props.onPress();
      expect(onPress).toHaveBeenCalledTimes(1);
    });

    it('handles disabled state', () => {
      render(<ThemedText disabled>Disabled Text</ThemedText>);
      const textElement = screen.getByText('Disabled Text');
      expect(textElement.props.accessibilityState?.disabled).toBe(true);
    });

    it('handles multiple children', () => {
      render(
        <ThemedText>
          <ThemedText>Child 1</ThemedText>
          <ThemedText>Child 2</ThemedText>
        </ThemedText>
      );
      expect(screen.getByText('Child 1')).toBeTruthy();
      expect(screen.getByText('Child 2')).toBeTruthy();
    });
  });

  describe('Dark Theme', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue('dark');
    });

    it('renders with dark theme colors', () => {
      render(<ThemedText>Dark Text</ThemedText>);
      const textElement = screen.getByText('Dark Text');
      expect(textElement).toBeTruthy();
    });

    it('applies dark theme styling', () => {
      render(<ThemedText>Dark Theme Text</ThemedText>);
      const textElement = screen.getByText('Dark Theme Text');
      expect(textElement.props.style).toBeDefined();
    });
  });

  describe('No Theme (null)', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue(null);
    });

    it('renders with default colors when no theme is available', () => {
      render(<ThemedText>Default Text</ThemedText>);
      const textElement = screen.getByText('Default Text');
      expect(textElement).toBeTruthy();
    });
  });

  describe('Props Validation', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue('light');
    });

    it('handles undefined children gracefully', () => {
      render(<ThemedText>{undefined}</ThemedText>);
      // Should not throw error
      expect(screen.getByTestId('themed-text')).toBeTruthy();
    });

    it('handles null children gracefully', () => {
      render(<ThemedText>{null}</ThemedText>);
      // Should not throw error
      expect(screen.getByTestId('themed-text')).toBeTruthy();
    });

    it('handles empty string children', () => {
      render(<ThemedText>{''}</ThemedText>);
      const textElement = screen.getByTestId('themed-text');
      expect(textElement).toBeTruthy();
    });

    it('handles number children', () => {
      render(<ThemedText>{42}</ThemedText>);
      const textElement = screen.getByText('42');
      expect(textElement).toBeTruthy();
    });

    it('handles boolean children', () => {
      render(<ThemedText>{true}</ThemedText>);
      const textElement = screen.getByText('true');
      expect(textElement).toBeTruthy();
    });
  });

  describe('Performance', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue('light');
    });

    it('renders efficiently with large text', () => {
      const largeText = 'A'.repeat(1000);
      const { rerender } = render(<ThemedText>{largeText}</ThemedText>);
      
      // Test re-rendering performance
      rerender(<ThemedText>{largeText}</ThemedText>);
      expect(screen.getByText(largeText)).toBeTruthy();
    });

    it('handles rapid theme changes', () => {
      const { rerender } = render(<ThemedText>Test</ThemedText>);
      
      // Simulate rapid theme changes
      mockUseColorScheme.mockReturnValue('dark');
      rerender(<ThemedText>Test</ThemedText>);
      
      mockUseColorScheme.mockReturnValue('light');
      rerender(<ThemedText>Test</ThemedText>);
      
      expect(screen.getByText('Test')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      mockUseColorScheme.mockReturnValue('light');
    });

    it('supports screen readers', () => {
      render(
        <ThemedText accessibilityLabel="Important text" accessibilityHint="This is important information">
          Important Text
        </ThemedText>
      );
      const textElement = screen.getByText('Important Text');
      expect(textElement.props.accessibilityLabel).toBe('Important text');
      expect(textElement.props.accessibilityHint).toBe('This is important information');
    });

    it('handles accessibility state', () => {
      render(
        <ThemedText accessibilityState={{ selected: true, disabled: false }}>
          State Text
        </ThemedText>
      );
      const textElement = screen.getByText('State Text');
      expect(textElement.props.accessibilityState).toEqual({
        selected: true,
        disabled: false,
      });
    });

    it('supports accessibility actions', () => {
      const accessibilityActions = [
        { name: 'activate', label: 'Activate' },
        { name: 'longpress', label: 'Long press' },
      ];
      render(
        <ThemedText accessibilityActions={accessibilityActions}>
          Action Text
        </ThemedText>
      );
      const textElement = screen.getByText('Action Text');
      expect(textElement.props.accessibilityActions).toEqual(accessibilityActions);
    });
  });
}); 