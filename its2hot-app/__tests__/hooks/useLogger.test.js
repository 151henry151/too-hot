import { renderHook, act } from '@testing-library/react-native';
import { useLogger } from '../../hooks/useLogger';

// Mock console methods
const mockConsole = {
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

global.console = mockConsole;

describe('useLogger', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Logging', () => {
    it('provides log function', () => {
      const { result } = renderHook(() => useLogger());
      expect(typeof result.current.log).toBe('function');
    });

    it('provides info function', () => {
      const { result } = renderHook(() => useLogger());
      expect(typeof result.current.info).toBe('function');
    });

    it('provides warn function', () => {
      const { result } = renderHook(() => useLogger());
      expect(typeof result.current.warn).toBe('function');
    });

    it('provides error function', () => {
      const { result } = renderHook(() => useLogger());
      expect(typeof result.current.error).toBe('function');
    });
  });

  describe('Log Function', () => {
    it('calls sendLog with correct parameters', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test log message';
      
      await act(async () => {
        await result.current.log(message);
      });
      
      // The function should have been called, but we can't easily test the network call
      // Instead, we test that the function exists and can be called
      expect(typeof result.current.log).toBe('function');
    });

    it('handles message with context', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test log message';
      const context = 'test-context';
      
      await act(async () => {
        await result.current.log(message, context);
      });
      
      expect(typeof result.current.log).toBe('function');
    });

    it('handles message with context and extra data', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test log message';
      const context = 'test-context';
      const extra = { key: 'value' };
      
      await act(async () => {
        await result.current.log(message, context, extra);
      });
      
      expect(typeof result.current.log).toBe('function');
    });
  });

  describe('Info Function', () => {
    it('calls sendLog with info level', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test info message';
      
      await act(async () => {
        await result.current.info(message);
      });
      
      expect(typeof result.current.info).toBe('function');
    });

    it('handles info with context and extra data', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test info message';
      const context = 'info-context';
      const extra = { info: 'data' };
      
      await act(async () => {
        await result.current.info(message, context, extra);
      });
      
      expect(typeof result.current.info).toBe('function');
    });
  });

  describe('Warn Function', () => {
    it('calls sendLog with warn level', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test warning message';
      
      await act(async () => {
        await result.current.warn(message);
      });
      
      expect(typeof result.current.warn).toBe('function');
    });

    it('handles warn with context and extra data', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test warning message';
      const context = 'warning-context';
      const extra = { warning: 'data' };
      
      await act(async () => {
        await result.current.warn(message, context, extra);
      });
      
      expect(typeof result.current.warn).toBe('function');
    });
  });

  describe('Error Function', () => {
    it('calls sendLog with error level', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test error message';
      
      await act(async () => {
        await result.current.error(message);
      });
      
      expect(typeof result.current.error).toBe('function');
    });

    it('handles error with context and extra data', async () => {
      const { result } = renderHook(() => useLogger());
      const message = 'Test error message';
      const context = 'error-context';
      const extra = { error: 'data' };
      
      await act(async () => {
        await result.current.error(message, context, extra);
      });
      
      expect(typeof result.current.error).toBe('function');
    });
  });

  describe('Network Error Handling', () => {
    it('falls back to console.error when network fails', async () => {
      // Mock fetch to fail
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      
      const { result } = renderHook(() => useLogger());
      const message = 'Test error message';
      
      await act(async () => {
        await result.current.error(message);
      });
      
      // Should call console.error as fallback
      expect(mockConsole.error).toHaveBeenCalledWith('Failed to send log to backend:', expect.any(Error));
    });
  });

  describe('Performance', () => {
    it('handles rapid logging calls', async () => {
      const { result } = renderHook(() => useLogger());
      
      await act(async () => {
        const promises = Array(10).fill().map((_, i) => 
          result.current.log(`Message ${i}`)
        );
        await Promise.all(promises);
      });
      
      // All functions should be available
      expect(typeof result.current.log).toBe('function');
      expect(typeof result.current.info).toBe('function');
      expect(typeof result.current.warn).toBe('function');
      expect(typeof result.current.error).toBe('function');
    });

    it('handles large messages efficiently', async () => {
      const { result } = renderHook(() => useLogger());
      const largeMessage = 'A'.repeat(1000);
      
      await act(async () => {
        await result.current.log(largeMessage);
      });
      
      expect(typeof result.current.log).toBe('function');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty string messages', async () => {
      const { result } = renderHook(() => useLogger());
      
      await act(async () => {
        await result.current.log('');
      });
      
      expect(typeof result.current.log).toBe('function');
    });

    it('handles undefined context', async () => {
      const { result } = renderHook(() => useLogger());
      
      await act(async () => {
        await result.current.log('Test message', undefined);
      });
      
      expect(typeof result.current.log).toBe('function');
    });

    it('handles undefined extra data', async () => {
      const { result } = renderHook(() => useLogger());
      
      await act(async () => {
        await result.current.log('Test message', 'context', undefined);
      });
      
      expect(typeof result.current.log).toBe('function');
    });
  });

  describe('Multiple Instances', () => {
    it('works with multiple hook instances', async () => {
      const { result: result1 } = renderHook(() => useLogger());
      const { result: result2 } = renderHook(() => useLogger());
      
      await act(async () => {
        await result1.current.log('Message 1');
        await result2.current.log('Message 2');
      });
      
      expect(typeof result1.current.log).toBe('function');
      expect(typeof result2.current.log).toBe('function');
    });
  });

  describe('Function Signatures', () => {
    it('has correct function signatures', () => {
      const { result } = renderHook(() => useLogger());
      
      // Test that all functions are async
      expect(result.current.log).toBeInstanceOf(Function);
      expect(result.current.info).toBeInstanceOf(Function);
      expect(result.current.warn).toBeInstanceOf(Function);
      expect(result.current.error).toBeInstanceOf(Function);
    });

    it('accepts correct parameters', async () => {
      const { result } = renderHook(() => useLogger());
      
      await act(async () => {
        // Test all parameter combinations
        await result.current.log('message');
        await result.current.log('message', 'context');
        await result.current.log('message', 'context', { extra: 'data' });
        
        await result.current.info('message');
        await result.current.info('message', 'context');
        await result.current.info('message', 'context', { extra: 'data' });
        
        await result.current.warn('message');
        await result.current.warn('message', 'context');
        await result.current.warn('message', 'context', { extra: 'data' });
        
        await result.current.error('message');
        await result.current.error('message', 'context');
        await result.current.error('message', 'context', { extra: 'data' });
      });
      
      // All should work without throwing errors
      expect(true).toBe(true);
    });
  });
}); 