import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
  Alert,
  TextInput,
  Platform,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useLogger, logError } from '../hooks/useLogger';
import PaymentService from '../services/PaymentService';
import { 
  ACCESSIBILITY, 
  createButtonAccessibility, 
  createTextAccessibility, 
  createImageAccessibility,
  createAccessibilityProps
} from '../utils/accessibility';

const { width } = Dimensions.get('window');

// Mock product data (you can replace with real data from your backend)
const products = {
  tshirt: {
    name: "IT'S TOO HOT! T-Shirt",
    description: "Wear this shirt when temperatures are 10°F+ hotter than average to raise climate awareness.",
    price: 25.00,
    colors: {
      black: {
        name: "Black",
        front: require('../assets/images/unisex-organic-mid-light-t-shirt-black-front-687da1fc27008.png'),
        back: require('../assets/images/unisex-organic-mid-light-t-shirt-black-back-687da1fc275a7.png'),
      },
      'french-navy': {
        name: "French Navy",
        front: require('../assets/images/unisex-organic-mid-light-t-shirt-french-navy-front-687da1fc26147.png'),
        back: require('../assets/images/unisex-organic-mid-light-t-shirt-french-navy-back-687da1fc26cdc.png'),
      },
      anthracite: {
        name: "Anthracite",
        front: require('../assets/images/unisex-organic-mid-light-t-shirt-anthracite-front-687da1fc279c8.png'),
        back: require('../assets/images/unisex-organic-mid-light-t-shirt-anthracite-back-687da1fc28199.png'),
      },
    },
  },
  tshirt_light: {
    name: "IT'S TOO HOT! T-Shirt (Light)",
    description: "Light design version for lighter colored shirts.",
    price: 25.00,
    colors: {
      white: {
        name: "White",
        front: require('../assets/images/unisex-organic-mid-light-t-shirt-white-front-687da29871c60.png'),
        back: require('../assets/images/unisex-organic-mid-light-t-shirt-white-back-687da2987241c.png'),
      },
      'heather-grey': {
        name: "Heather Grey",
        front: require('../assets/images/unisex-organic-mid-light-t-shirt-heather-grey-front-687da298707b3.png'),
        back: require('../assets/images/unisex-organic-mid-light-t-shirt-heather-grey-back-687da298712d1.png'),
      },
    },
  },
};

const sizes = [
  { value: 'S', label: 'Small' },
  { value: 'M', label: 'Medium' },
  { value: 'L', label: 'Large' },
  { value: 'XL', label: 'X-Large' },
  { value: 'XXL', label: 'XX-Large' },
];

export default function ShopScreen() {
  const [selectedDesign, setSelectedDesign] = useState('tshirt');
  const [selectedColor, setSelectedColor] = useState('black');
  const [selectedSize, setSelectedSize] = useState('M');
  const [selectedView, setSelectedView] = useState('front');
  const [quantity, setQuantity] = useState(1);
  const logger = useLogger();

  const currentProduct = products[selectedDesign];
  const currentColor = currentProduct.colors[selectedColor];
  


  const handleBuyPress = async () => {
    const total = (currentProduct.price * quantity).toFixed(2);
    const orderData = {
      product: currentProduct.name,
      color: currentColor.name,
      size: selectedSize,
      quantity: quantity,
      total: total
    };

    logger.log('User initiated purchase', 'Shop', orderData);

    try {
      // Check if payment is supported
      if (!PaymentService.isSupported) {
        Alert.alert('Payment Not Available', 'Payment is not available on this device.');
        return;
      }

      // Show order confirmation
      Alert.alert(
        'Purchase Confirmation',
        `Order Summary:\n\nDesign: ${currentProduct.name}\nColor: ${currentColor.name}\nSize: ${selectedSize}\nQuantity: ${quantity}\nTotal: $${total}\n\nProceed with ${Platform.OS === 'ios' ? 'Apple Pay' : Platform.OS === 'android' ? 'Google Pay' : 'web checkout'}?\n\nPayment will be processed securely through PayPal.`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => logger.info('User cancelled purchase', 'Shop'),
          },
          {
            text: 'Buy Now',
            onPress: async () => {
              await processPurchase(orderData);
            },
          },
        ]
      );
    } catch (error) {
      logger.error('Error during purchase flow: ' + (error?.toString?.() || String(error)), 'Shop Exception');
      Alert.alert('Error', 'An error occurred while processing your purchase. Please try again.');
    }
  };

  const processPurchase = async (orderData) => {
    try {
      logger.log('Processing payment', 'Shop', { method: Platform.OS === 'ios' ? 'Apple Pay' : Platform.OS === 'android' ? 'Google Pay' : 'Web' });

      // Create order on backend
      const orderResult = await PaymentService.createOrder(orderData);
      logger.log('Order created', 'Shop', { orderId: orderResult.order_id });

      // Process payment
      const paymentResult = await PaymentService.processPayment(orderData);
      logger.log('Payment processed', 'Shop', { 
        transactionId: paymentResult.transactionId,
        method: paymentResult.method 
      });

      // Confirm order with payment result
      const confirmResult = await PaymentService.confirmOrder(orderResult.order_id, paymentResult);
      logger.log('Order confirmed', 'Shop', { orderId: confirmResult.order_id });

      // Show success message
      Alert.alert(
        'Payment Successful!',
        `Your order has been placed successfully.\n\nOrder ID: ${confirmResult.order_id}\nTransaction ID: ${paymentResult.transactionId}\n\nYour shirt will ship in 2-3 business days.`,
        [{ text: 'OK' }]
      );

    } catch (error) {
      logger.error('Purchase processing error: ' + (error?.toString?.() || String(error)), 'Shop Exception');
      
      if (error.message === 'Payment cancelled') {
        Alert.alert('Payment Cancelled', 'Your payment was cancelled.');
      } else {
        Alert.alert('Payment Error', 'An error occurred while processing your payment. Please try again.');
      }
    }
  };

  const increaseQuantity = () => {
    if (quantity < 10) {
      setQuantity(quantity + 1);
    }
  };

  const decreaseQuantity = () => {
    if (quantity > 1) {
      setQuantity(quantity - 1);
    }
  };

  return (
    <ScrollView 
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      {...createAccessibilityProps(
        'Shop screen for purchasing IT\'S TOO HOT! t-shirts',
        'Scroll to view all product options and purchase details'
      )}
    >
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <Text 
          style={styles.heroTitle}
          {...createTextAccessibility('Get Your IT\'S TOO HOT! T-Shirt', ACCESSIBILITY.ROLES.HEADER)}
        >
          Get Your "IT'S TOO HOT!" T-Shirt
        </Text>
        <Text 
          style={styles.heroSubtitle}
          {...createTextAccessibility('Wear the shirt when you get the alert to raise climate awareness')}
        >
          Wear the shirt when you get the alert.
        </Text>
      </View>

      {/* Product Display */}
      <View style={styles.productSection}>
        <View style={styles.productImageContainer}>
          <Image
            source={selectedView === 'front' ? currentColor.front : currentColor.back}
            style={styles.productImage}
            resizeMode="contain"
            {...createImageAccessibility(`${selectedView} view of ${currentColor.name} ${currentProduct.name}`)}
          />
          
          {/* View Toggle Buttons */}
          <View style={styles.viewToggleContainer}>
            <TouchableOpacity
              style={[styles.viewButton, selectedView === 'front' && styles.viewButtonActive]}
              onPress={() => setSelectedView('front')}
              {...createButtonAccessibility(
                ACCESSIBILITY.LABELS.VIEW_FRONT,
                ACCESSIBILITY.HINTS.VIEW_FRONT,
                selectedView === 'front'
              )}
            >
              <Text style={[styles.viewButtonText, selectedView === 'front' && styles.viewButtonTextActive]}>
                Front
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.viewButton, selectedView === 'back' && styles.viewButtonActive]}
              onPress={() => setSelectedView('back')}
              {...createButtonAccessibility(
                ACCESSIBILITY.LABELS.VIEW_BACK,
                ACCESSIBILITY.HINTS.VIEW_BACK,
                selectedView === 'back'
              )}
            >
              <Text style={[styles.viewButtonText, selectedView === 'back' && styles.viewButtonTextActive]}>
                Back
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Product Details */}
        <View style={styles.detailsSection}>
          <Text 
            style={styles.productName}
            {...createTextAccessibility(currentProduct.name, ACCESSIBILITY.ROLES.HEADER)}
          >
            {currentProduct.name}
          </Text>
          <Text 
            style={styles.productDescription}
            {...createTextAccessibility(currentProduct.description)}
          >
            {currentProduct.description}
          </Text>

          {/* Design Selection */}
          <View style={styles.optionSection}>
            <Text 
              style={styles.optionLabel}
              {...createTextAccessibility('Design Selection', ACCESSIBILITY.ROLES.HEADER)}
            >
              Design
            </Text>
            <View style={styles.designButtons}>
              <TouchableOpacity
                style={[styles.designButton, selectedDesign === 'tshirt' && styles.designButtonActive]}
                onPress={() => {
                  setSelectedDesign('tshirt');
                  setSelectedColor('black');
                }}
                {...createButtonAccessibility(
                  'Dark Design - White text on dark background',
                  ACCESSIBILITY.HINTS.DESIGN_SELECTION,
                  selectedDesign === 'tshirt'
                )}
              >
                <Text style={[styles.designButtonText, selectedDesign === 'tshirt' && styles.designButtonTextActive]}>
                  Dark Design
                </Text>
                <Text style={styles.designButtonSubtext}>White text on dark</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.designButton, selectedDesign === 'tshirt_light' && styles.designButtonActive]}
                onPress={() => {
                  setSelectedDesign('tshirt_light');
                  setSelectedColor('white');
                }}
                {...createButtonAccessibility(
                  'Light Design - Black text on light background',
                  ACCESSIBILITY.HINTS.DESIGN_SELECTION,
                  selectedDesign === 'tshirt_light'
                )}
              >
                <Text style={[styles.designButtonText, selectedDesign === 'tshirt_light' && styles.designButtonTextActive]}>
                  Light Design
                </Text>
                <Text style={styles.designButtonSubtext}>Black text on light</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Color Selection */}
          <View style={styles.optionSection}>
            <Text 
              style={styles.optionLabel}
              {...createTextAccessibility('Color Selection', ACCESSIBILITY.ROLES.HEADER)}
            >
              Color
            </Text>
            <View style={styles.colorGrid}>
              {Object.keys(currentProduct.colors).map((colorKey) => (
                <TouchableOpacity
                  key={colorKey}
                  style={[styles.colorButton, selectedColor === colorKey && styles.colorButtonActive]}
                  onPress={() => setSelectedColor(colorKey)}
                  {...createButtonAccessibility(
                    `${currentProduct.colors[colorKey].name} color`,
                    ACCESSIBILITY.HINTS.COLOR_SELECTION,
                    selectedColor === colorKey
                  )}
                >
                  <Text style={[styles.colorButtonText, selectedColor === colorKey && styles.colorButtonTextActive]}>
                    {currentProduct.colors[colorKey].name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Features */}
          <View style={styles.featuresList}>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#10b981" />
              <Text 
                style={styles.featureText}
                {...createTextAccessibility('100% Cotton material')}
              >
                100% Cotton
              </Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#10b981" />
              <Text 
                style={styles.featureText}
                {...createTextAccessibility('Multiple sizes available')}
              >
                Multiple sizes available
              </Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={20} color="#10b981" />
              <Text 
                style={styles.featureText}
                {...createTextAccessibility('Fast shipping')}
              >
                Fast shipping
              </Text>
            </View>
          </View>

          {/* Price */}
          <Text 
            style={styles.price}
            {...createTextAccessibility(`Price: $${currentProduct.price.toFixed(2)}`)}
          >
            ${currentProduct.price.toFixed(2)}
          </Text>

          {/* Size Selection */}
          <View style={styles.optionSection}>
            <Text 
              style={styles.optionLabel}
              {...createTextAccessibility('Size Selection', ACCESSIBILITY.ROLES.HEADER)}
            >
              Size
            </Text>
            <View style={styles.sizeGrid}>
              {sizes.map((size) => (
                <TouchableOpacity
                  key={size.value}
                  style={[styles.sizeButton, selectedSize === size.value && styles.sizeButtonActive]}
                  onPress={() => setSelectedSize(size.value)}
                  {...createButtonAccessibility(
                    `${size.label} size`,
                    ACCESSIBILITY.HINTS.SIZE_SELECTION,
                    selectedSize === size.value
                  )}
                >
                  <Text style={[styles.sizeButtonText, selectedSize === size.value && styles.sizeButtonTextActive]}>
                    {size.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Quantity Selection */}
          <View style={styles.optionSection}>
            <Text 
              style={styles.optionLabel}
              {...createTextAccessibility('Quantity Selection', ACCESSIBILITY.ROLES.HEADER)}
            >
              Quantity
            </Text>
            <View style={styles.quantityContainer}>
              <TouchableOpacity
                style={[styles.quantityButton, quantity <= 1 && styles.quantityButtonDisabled]}
                onPress={decreaseQuantity}
                disabled={quantity <= 1}
                {...createButtonAccessibility(
                  ACCESSIBILITY.LABELS.QUANTITY_DECREASE,
                  ACCESSIBILITY.HINTS.QUANTITY_DECREASE,
                  quantity <= 1
                )}
              >
                <Ionicons name="remove" size={20} color={quantity <= 1 ? "#ccc" : "#000"} />
              </TouchableOpacity>
              
              <Text 
                style={styles.quantityText}
                {...createTextAccessibility(`${quantity} selected`, ACCESSIBILITY.ROLES.TEXT)}
              >
                {quantity}
              </Text>
              
              <TouchableOpacity
                style={[styles.quantityButton, quantity >= 10 && styles.quantityButtonDisabled]}
                onPress={increaseQuantity}
                disabled={quantity >= 10}
                {...createButtonAccessibility(
                  ACCESSIBILITY.LABELS.QUANTITY_INCREASE,
                  ACCESSIBILITY.HINTS.QUANTITY_INCREASE,
                  quantity >= 10
                )}
              >
                <Ionicons name="add" size={20} color={quantity >= 10 ? "#ccc" : "#000"} />
              </TouchableOpacity>
            </View>
          </View>

          {/* Total */}
          <View style={styles.totalSection}>
            <Text 
              style={styles.totalLabel}
              {...createTextAccessibility('Total price')}
            >
              Total:
            </Text>
            <Text 
              style={styles.totalAmount}
              {...createTextAccessibility(`$${(currentProduct.price * quantity).toFixed(2)}`)}
            >
              ${(currentProduct.price * quantity).toFixed(2)}
            </Text>
          </View>

          {/* Buy Button */}
          <TouchableOpacity
            style={styles.buyButton}
            onPress={handleBuyPress}
            {...createButtonAccessibility(
              ACCESSIBILITY.LABELS.BUY_BUTTON,
              ACCESSIBILITY.HINTS.BUY_BUTTON
            )}
          >
            <Ionicons name="cart" size={20} color="white" />
            <Text style={styles.buyButtonText}>Buy Now</Text>
          </TouchableOpacity>

          {/* Web Shop Link */}
          <TouchableOpacity
            style={styles.webShopLink}
            onPress={() => Linking.openURL('https://its2hot.org/shop')}
            {...createButtonAccessibility(
              'Open web shop',
              'Opens the full web shop in your browser for alternative purchase options'
            )}
          >
            <Ionicons name="globe-outline" size={16} color="#3b82f6" />
            <Text style={styles.webShopLinkText}>Prefer to shop online?</Text>
            <Ionicons name="open-outline" size={16} color="#3b82f6" />
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  contentContainer: {
    paddingBottom: 20, // Add some padding at the bottom for the buy button
  },
  heroSection: {
    backgroundColor: 'white',
    paddingVertical: 24,
    paddingHorizontal: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
  },
  productSection: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  productImageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  productImage: {
    width: width * 0.7,
    height: 300,
    marginBottom: 16,
  },
  viewToggleContainer: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    padding: 4,
  },
  viewButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  viewButtonActive: {
    backgroundColor: '#3b82f6',
  },
  viewButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  viewButtonTextActive: {
    color: 'white',
  },
  detailsSection: {
    flex: 1,
  },
  productName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  productDescription: {
    fontSize: 16,
    color: '#6b7280',
    lineHeight: 24,
    marginBottom: 20,
  },
  optionSection: {
    marginBottom: 20,
  },
  optionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  designButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  designButton: {
    flex: 1,
    padding: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#d1d5db',
    backgroundColor: 'white',
  },
  designButtonActive: {
    backgroundColor: '#1f2937',
    borderColor: '#1f2937',
  },
  designButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  designButtonTextActive: {
    color: 'white',
  },
  designButtonSubtext: {
    fontSize: 12,
    color: '#6b7280',
  },
  colorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  colorButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#d1d5db',
    backgroundColor: 'white',
  },
  colorButtonActive: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  colorButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  colorButtonTextActive: {
    color: 'white',
  },
  featuresList: {
    marginBottom: 20,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 20,
  },
  sizeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  sizeButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#d1d5db',
    backgroundColor: 'white',
  },
  sizeButtonActive: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  sizeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  sizeButtonTextActive: {
    color: 'white',
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  quantityButton: {
    width: 40,
    height: 40,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  quantityButtonDisabled: {
    opacity: 0.5,
  },
  quantityText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    minWidth: 40,
    textAlign: 'center',
  },
  totalSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  buyButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  buyButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  webShopLink: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginTop: 8,
    borderRadius: 8,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  webShopLinkText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
    marginHorizontal: 8,
  },
  secureText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  featuresSection: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  featureCard: {
    flex: 1,
    minWidth: width * 0.4,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  featureCardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 12,
    marginBottom: 8,
    textAlign: 'center',
  },
  featureCardText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
}); 