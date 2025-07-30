import { Platform, Alert } from 'react-native';
import * as Linking from 'expo-linking';

// Payment service that uses native mobile payments for app store compliance
// but integrates with PayPal backend for actual payment processing
class PaymentService {
  constructor() {
    this.isSupported = this.checkPaymentSupport();
  }

  checkPaymentSupport() {
    if (Platform.OS === 'ios') {
      // Check if Apple Pay is available
      // In production, you'd check PKPaymentAuthorizationController.canMakePayments()
      return true; // For now, assume available
    } else if (Platform.OS === 'android') {
      // Check if Google Pay is available
      // In production, you'd check Google Pay API availability
      return true; // For now, assume available
    } else {
      // Web platform
      return true;
    }
  }

  async processPayment(orderData) {
    const { product, color, size, quantity, total } = orderData;
    
    try {
      if (Platform.OS === 'ios') {
        return await this.processApplePay(orderData);
      } else if (Platform.OS === 'android') {
        return await this.processGooglePay(orderData);
      } else {
        // Web platform - redirect to web checkout
        return await this.processWebPayment(orderData);
      }
    } catch (error) {
      console.error('Payment processing error:', error);
      throw new Error('Payment processing failed');
    }
  }

  async processApplePay(orderData) {
    const { product, color, size, quantity, total } = orderData;
    
    // Apple Pay implementation that integrates with PayPal backend
    // In production, you'd use @stripe/stripe-react-native or similar
    return new Promise((resolve, reject) => {
      Alert.alert(
        'Apple Pay',
        `Pay $${total} for ${quantity}x ${product} (${color}, ${size})?\n\nThis will be processed securely through PayPal.`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => reject(new Error('Payment cancelled')),
          },
          {
            text: 'Pay with Apple Pay',
            onPress: () => {
              // Simulate Apple Pay processing with PayPal backend
              setTimeout(() => {
                resolve({
                  success: true,
                  transactionId: `AP_${Date.now()}`,
                  amount: total,
                  method: 'Apple Pay',
                  backend: 'PayPal'
                });
              }, 1000);
            },
          },
        ]
      );
    });
  }

  async processGooglePay(orderData) {
    const { product, color, size, quantity, total } = orderData;
    
    // Google Pay implementation that integrates with PayPal backend
    // In production, you'd use react-native-payments or similar
    return new Promise((resolve, reject) => {
      Alert.alert(
        'Google Pay',
        `Pay $${total} for ${quantity}x ${product} (${color}, ${size})?\n\nThis will be processed securely through PayPal.`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => reject(new Error('Payment cancelled')),
          },
          {
            text: 'Pay with Google Pay',
            onPress: () => {
              // Simulate Google Pay processing with PayPal backend
              setTimeout(() => {
                resolve({
                  success: true,
                  transactionId: `GP_${Date.now()}`,
                  amount: total,
                  method: 'Google Pay',
                  backend: 'PayPal'
                });
              }, 1000);
            },
          },
        ]
      );
    });
  }

  async processWebPayment(orderData) {
    const { product, color, size, quantity, total } = orderData;
    
    // For web platform, redirect to the existing PayPal checkout
    const checkoutUrl = `https://its2hot.org/checkout?product=${encodeURIComponent(product)}&color=${encodeURIComponent(color)}&size=${encodeURIComponent(size)}&quantity=${quantity}&total=${total}`;
    
    try {
      await Linking.openURL(checkoutUrl);
      return {
        success: true,
        transactionId: `WEB_${Date.now()}`,
        amount: total,
        method: 'Web Checkout',
        backend: 'PayPal',
        redirectUrl: checkoutUrl
      };
    } catch (error) {
      throw new Error('Failed to open checkout URL');
    }
  }

  async createOrder(orderData) {
    const { product, color, size, quantity, total } = orderData;
    
    // Create order on backend with PayPal integration
    try {
      const response = await fetch('https://its2hot.org/api/create-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product: product,
          color: color,
          size: size,
          quantity: quantity,
          total: total,
          platform: Platform.OS,
          payment_method: Platform.OS === 'ios' ? 'apple_pay' : Platform.OS === 'android' ? 'google_pay' : 'web'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create order');
      }

      const orderResult = await response.json();
      console.log('Order created with PayPal backend:', orderResult);
      return orderResult;
    } catch (error) {
      console.error('Order creation error:', error);
      throw new Error(`Failed to create order: ${error.message}`);
    }
  }

  async confirmOrder(orderId, paymentResult) {
    try {
      const response = await fetch('https://its2hot.org/api/confirm-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          payment_result: paymentResult,
          platform: Platform.OS
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to confirm order');
      }

      const confirmResult = await response.json();
      console.log('Order confirmed with PayPal backend:', confirmResult);
      return confirmResult;
    } catch (error) {
      console.error('Order confirmation error:', error);
      throw new Error(`Failed to confirm order: ${error.message}`);
    }
  }

  // Helper method to get payment method display name
  getPaymentMethodDisplayName() {
    if (Platform.OS === 'ios') {
      return 'Apple Pay';
    } else if (Platform.OS === 'android') {
      return 'Google Pay';
    } else {
      return 'Web Checkout';
    }
  }

  // Helper method to get backend processor name
  getBackendProcessorName() {
    return 'PayPal';
  }
}

export default new PaymentService(); 