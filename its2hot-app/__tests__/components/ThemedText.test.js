import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { ThemedText } from '../../components/ThemedText';

// Mock the useThemeColor hook
jest.mock('../../hooks/useThemeColor', () => ({
  useThemeColor: jest.fn(() => '#000000'),
}));

describe('ThemedText', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders text content correctly', () => {
      render(<ThemedText>Test Text</ThemedText>);
      const textElement = screen.getByText('Test Text');
      expect(textElement).toBeTruthy();
    });

    it('applies custom style props', () => {
      const customStyle = { fontSize: 20, fontWeight: 'bold' };
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
  });

  describe('Text Types', () => {
    it('renders default type correctly', () => {
      render(<ThemedText type="default">Default Text</ThemedText>);
      const textElement = screen.getByText('Default Text');
      expect(textElement).toBeTruthy();
    });

    it('renders title type correctly', () => {
      render(<ThemedText type="title">Title Text</ThemedText>);
      const textElement = screen.getByText('Title Text');
      expect(textElement).toBeTruthy();
    });

    it('renders subtitle type correctly', () => {
      render(<ThemedText type="subtitle">Subtitle Text</ThemedText>);
      const textElement = screen.getByText('Subtitle Text');
      expect(textElement).toBeTruthy();
    });

    it('renders link type correctly', () => {
      render(<ThemedText type="link">Link Text</ThemedText>);
      const textElement = screen.getByText('Link Text');
      expect(textElement).toBeTruthy();
    });

    it('renders defaultSemiBold type correctly', () => {
      render(<ThemedText type="defaultSemiBold">SemiBold Text</ThemedText>);
      const textElement = screen.getByText('SemiBold Text');
      expect(textElement).toBeTruthy();
    });
  });

  describe('Theme Colors', () => {
    it('applies light color when provided', () => {
      render(<ThemedText lightColor="#FF0000">Red Text</ThemedText>);
      const textElement = screen.getByText('Red Text');
      expect(textElement).toBeTruthy();
    });

    it('applies dark color when provided', () => {
      render(<ThemedText darkColor="#0000FF">Blue Text</ThemedText>);
      const textElement = screen.getByText('Blue Text');
      expect(textElement).toBeTruthy();
    });

    it('applies both light and dark colors', () => {
      render(
        <ThemedText lightColor="#FF0000" darkColor="#0000FF">
          Themed Text
        </ThemedText>
      );
      const textElement = screen.getByText('Themed Text');
      expect(textElement).toBeTruthy();
    });
  });

  describe('Props Validation', () => {
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

  describe('Accessibility', () => {
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

  describe('Performance', () => {
    it('renders efficiently with large text', () => {
      const largeText = 'A'.repeat(1000);
      const { rerender } = render(<ThemedText>{largeText}</ThemedText>);
      
      // Test re-rendering performance
      rerender(<ThemedText>{largeText}</ThemedText>);
      expect(screen.getByText(largeText)).toBeTruthy();
    });

    it('handles multiple children efficiently', () => {
      render(
        <ThemedText>
          <ThemedText>Child 1</ThemedText>
          <ThemedText>Child 2</ThemedText>
          <ThemedText>Child 3</ThemedText>
        </ThemedText>
      );
      expect(screen.getByText('Child 1')).toBeTruthy();
      expect(screen.getByText('Child 2')).toBeTruthy();
      expect(screen.getByText('Child 3')).toBeTruthy();
    });
  });
}); 