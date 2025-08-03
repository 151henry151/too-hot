import { PaymentService } from '../../services/PaymentService';

// Mock Stripe
const mockStripe = {
  initPaymentSheet: jest.fn(),
  presentPaymentSheet: jest.fn(),
  createPaymentMethod: jest.fn(),
};

jest.mock('@stripe/stripe-react-native', () => ({
  useStripe: () => mockStripe,
}));

// Mock fetch
global.fetch = jest.fn();

describe('PaymentService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  describe('initializePayment', () => {
    it('successfully initializes payment sheet', async () => {
      const mockResponse = {
        paymentIntent: 'pi_test_123',
        ephemeralKey: 'ek_test_123',
        customer: 'cus_test_123',
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      mockStripe.initPaymentSheet.mockResolvedValueOnce({ error: null });

      const result = await PaymentService.initializePayment(1000, 'USD');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/create-payment-intent'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            amount: 1000,
            currency: 'USD',
          }),
        })
      );

      expect(mockStripe.initPaymentSheet).toHaveBeenCalledWith({
        merchantDisplayName: expect.any(String),
        paymentIntentClientSecret: mockResponse.paymentIntent,
        customerEphemeralKeySecret: mockResponse.ephemeralKey,
        customerId: mockResponse.customer,
      });

      expect(result.success).toBe(true);
      expect(result.error).toBeNull();
    });

    it('handles API error during initialization', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ error: 'Invalid amount' }),
      });

      const result = await PaymentService.initializePayment(-100, 'USD');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid amount');
      expect(mockStripe.initPaymentSheet).not.toHaveBeenCalled();
    });

    it('handles network error during initialization', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await PaymentService.initializePayment(1000, 'USD');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });

    it('handles Stripe initialization error', async () => {
      const mockResponse = {
        paymentIntent: 'pi_test_123',
        ephemeralKey: 'ek_test_123',
        customer: 'cus_test_123',
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      mockStripe.initPaymentSheet.mockResolvedValueOnce({
        error: { message: 'Stripe initialization failed' },
      });

      const result = await PaymentService.initializePayment(1000, 'USD');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Stripe initialization failed');
    });
  });

  describe('processPayment', () => {
    it('successfully processes payment', async () => {
      mockStripe.presentPaymentSheet.mockResolvedValueOnce({ error: null });

      const result = await PaymentService.processPayment();

      expect(mockStripe.presentPaymentSheet).toHaveBeenCalled();
      expect(result.success).toBe(true);
      expect(result.error).toBeNull();
    });

    it('handles payment cancellation', async () => {
      mockStripe.presentPaymentSheet.mockResolvedValueOnce({
        error: { code: 'Canceled' },
      });

      const result = await PaymentService.processPayment();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Payment was canceled');
    });

    it('handles payment failure', async () => {
      mockStripe.presentPaymentSheet.mockResolvedValueOnce({
        error: { message: 'Payment failed' },
      });

      const result = await PaymentService.processPayment();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Payment failed');
    });

    it('handles unknown payment error', async () => {
      mockStripe.presentPaymentSheet.mockResolvedValueOnce({
        error: { code: 'UnknownError' },
      });

      const result = await PaymentService.processPayment();

      expect(result.success).toBe(false);
      expect(result.error).toBe('An unknown error occurred');
    });
  });

  describe('createPaymentMethod', () => {
    it('successfully creates payment method', async () => {
      const mockPaymentMethod = {
        id: 'pm_test_123',
        type: 'card',
      };

      mockStripe.createPaymentMethod.mockResolvedValueOnce({
        paymentMethod: mockPaymentMethod,
        error: null,
      });

      const result = await PaymentService.createPaymentMethod({
        type: 'card',
        billingDetails: {
          name: 'John Doe',
          email: 'john@example.com',
        },
      });

      expect(mockStripe.createPaymentMethod).toHaveBeenCalledWith({
        type: 'card',
        billingDetails: {
          name: 'John Doe',
          email: 'john@example.com',
        },
      });

      expect(result.success).toBe(true);
      expect(result.paymentMethod).toEqual(mockPaymentMethod);
      expect(result.error).toBeNull();
    });

    it('handles payment method creation error', async () => {
      mockStripe.createPaymentMethod.mockResolvedValueOnce({
        paymentMethod: null,
        error: { message: 'Invalid card details' },
      });

      const result = await PaymentService.createPaymentMethod({
        type: 'card',
        billingDetails: {
          name: 'John Doe',
          email: 'john@example.com',
        },
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid card details');
      expect(result.paymentMethod).toBeNull();
    });
  });

  describe('validatePaymentData', () => {
    it('validates correct payment data', () => {
      const validData = {
        amount: 1000,
        currency: 'USD',
        description: 'Test payment',
      };

      const result = PaymentService.validatePaymentData(validData);

      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    it('validates amount requirements', () => {
      const invalidData = {
        amount: -100,
        currency: 'USD',
        description: 'Test payment',
      };

      const result = PaymentService.validatePaymentData(invalidData);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Amount must be greater than 0');
    });

    it('validates currency requirements', () => {
      const invalidData = {
        amount: 1000,
        currency: '',
        description: 'Test payment',
      };

      const result = PaymentService.validatePaymentData(invalidData);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Currency is required');
    });

    it('validates description requirements', () => {
      const invalidData = {
        amount: 1000,
        currency: 'USD',
        description: '',
      };

      const result = PaymentService.validatePaymentData(invalidData);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Description is required');
    });

    it('returns multiple validation errors', () => {
      const invalidData = {
        amount: -100,
        currency: '',
        description: '',
      };

      const result = PaymentService.validatePaymentData(invalidData);

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(3);
      expect(result.errors).toContain('Amount must be greater than 0');
      expect(result.errors).toContain('Currency is required');
      expect(result.errors).toContain('Description is required');
    });
  });

  describe('formatCurrency', () => {
    it('formats USD currency correctly', () => {
      const result = PaymentService.formatCurrency(1000, 'USD');
      expect(result).toBe('$10.00');
    });

    it('formats EUR currency correctly', () => {
      const result = PaymentService.formatCurrency(1500, 'EUR');
      expect(result).toBe('€15.00');
    });

    it('handles zero amount', () => {
      const result = PaymentService.formatCurrency(0, 'USD');
      expect(result).toBe('$0.00');
    });

    it('handles large amounts', () => {
      const result = PaymentService.formatCurrency(999999, 'USD');
      expect(result).toBe('$9,999.99');
    });
  });

  describe('Error Handling', () => {
    it('handles undefined Stripe instance', async () => {
      // Mock useStripe to return undefined
      jest.doMock('@stripe/stripe-react-native', () => ({
        useStripe: () => undefined,
      }));

      const result = await PaymentService.processPayment();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Stripe is not initialized');
    });

    it('handles missing payment intent', async () => {
      const mockResponse = {
        paymentIntent: null,
        ephemeralKey: 'ek_test_123',
        customer: 'cus_test_123',
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await PaymentService.initializePayment(1000, 'USD');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid payment intent response');
    });
  });

  describe('Performance', () => {
    it('handles rapid payment attempts', async () => {
      mockStripe.presentPaymentSheet.mockResolvedValue({ error: null });

      const promises = Array(5).fill().map(() => PaymentService.processPayment());
      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });

    it('handles concurrent payment initializations', async () => {
      const mockResponse = {
        paymentIntent: 'pi_test_123',
        ephemeralKey: 'ek_test_123',
        customer: 'cus_test_123',
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      mockStripe.initPaymentSheet.mockResolvedValue({ error: null });

      const promises = Array(3).fill().map(() => 
        PaymentService.initializePayment(1000, 'USD')
      );
      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });
  });
}); 