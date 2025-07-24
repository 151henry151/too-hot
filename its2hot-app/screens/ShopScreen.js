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
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useLogger, logError } from '../hooks/useLogger';

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
  


  const handleBuyPress = () => {
    const total = (currentProduct.price * quantity).toFixed(2);
    logger.log('User initiated purchase', 'Shop', { product: currentProduct.name, color: currentColor.name, size: selectedSize, quantity, total });
    try {
      Alert.alert(
        'Purchase Confirmation',
        `Order Summary:\n\nDesign: ${currentProduct.name}\nColor: ${currentColor.name}\nSize: ${selectedSize}\nQuantity: ${quantity}\nTotal: $${total}\n\nProceed to PayPal?`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => logger.info('User cancelled purchase', 'Shop'),
          },
          {
            text: 'Buy Now',
            onPress: () => {
              logger.log('User confirmed purchase, redirecting to PayPal', 'Shop');
              // Here you would integrate with your PayPal backend
              Alert.alert(
                'Redirecting to PayPal',
                'You will be redirected to PayPal to complete your purchase.',
                [
                  {
                    text: 'OK',
                    onPress: () => {
                      // Mock PayPal redirect
                      logger.log('Mock PayPal payment completed', 'Shop');
                      Alert.alert('Success', 'Payment completed! Your shirt will ship in 2-3 business days.');
                    },
                  },
                ]
              );
            },
          },
        ]
      );
    } catch (error) {
      logger.error('Error during purchase flow: ' + (error?.toString?.() || String(error)), 'Shop Exception');
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
    <ScrollView style={styles.container}>
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <Text style={styles.heroTitle}>Get Your "IT'S TOO HOT!" T-Shirt</Text>
        <Text style={styles.heroSubtitle}>Wear the shirt when you get the alert.</Text>
      </View>

      {/* Product Section */}
      <View style={styles.productCard}>
        <View style={styles.productGrid}>
          {/* Product Image */}
          <View style={styles.imageSection}>
            <Image
              source={selectedView === 'front' ? currentColor.front : currentColor.back}
              style={styles.productImage}
              resizeMode="contain"
              key={`${selectedDesign}-${selectedColor}-${selectedView}`}
            />
            
            {/* View Toggle */}
            <View style={styles.viewToggle}>
              <TouchableOpacity
                style={[styles.viewButton, selectedView === 'front' && styles.viewButtonActive]}
                onPress={() => setSelectedView('front')}
              >
                <Text style={[styles.viewButtonText, selectedView === 'front' && styles.viewButtonTextActive]}>
                  Front
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.viewButton, selectedView === 'back' && styles.viewButtonActive]}
                onPress={() => setSelectedView('back')}
              >
                <Text style={[styles.viewButtonText, selectedView === 'back' && styles.viewButtonTextActive]}>
                  Back
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Product Details */}
          <View style={styles.detailsSection}>
            <Text style={styles.productName}>{currentProduct.name}</Text>
            <Text style={styles.productDescription}>{currentProduct.description}</Text>

            {/* Design Selection */}
            <View style={styles.optionSection}>
              <Text style={styles.optionLabel}>Design</Text>
              <View style={styles.designButtons}>
                <TouchableOpacity
                  style={[styles.designButton, selectedDesign === 'tshirt' && styles.designButtonActive]}
                  onPress={() => {
                    setSelectedDesign('tshirt');
                    setSelectedColor('black');
                  }}
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
              <Text style={styles.optionLabel}>Color</Text>
              <View style={styles.colorGrid}>
                {Object.keys(currentProduct.colors).map((colorKey) => (
                  <TouchableOpacity
                    key={colorKey}
                    style={[styles.colorButton, selectedColor === colorKey && styles.colorButtonActive]}
                    onPress={() => setSelectedColor(colorKey)}
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
                <Text style={styles.featureText}>100% Cotton</Text>
              </View>
              <View style={styles.featureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#10b981" />
                <Text style={styles.featureText}>Multiple sizes available</Text>
              </View>
              <View style={styles.featureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#10b981" />
                <Text style={styles.featureText}>Fast shipping</Text>
              </View>
            </View>

            {/* Price */}
            <Text style={styles.price}>${currentProduct.price.toFixed(2)}</Text>

            {/* Size Selection */}
            <View style={styles.optionSection}>
              <Text style={styles.optionLabel}>Size</Text>
              <View style={styles.sizeGrid}>
                {sizes.map((size) => (
                  <TouchableOpacity
                    key={size.value}
                    style={[styles.sizeButton, selectedSize === size.value && styles.sizeButtonActive]}
                    onPress={() => setSelectedSize(size.value)}
                  >
                    <Text style={[styles.sizeButtonText, selectedSize === size.value && styles.sizeButtonTextActive]}>
                      {size.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Quantity */}
            <View style={styles.optionSection}>
              <Text style={styles.optionLabel}>Quantity</Text>
              <View style={styles.quantityControls}>
                <TouchableOpacity style={styles.quantityButton} onPress={decreaseQuantity}>
                  <Ionicons name="remove" size={20} color="#6b7280" />
                </TouchableOpacity>
                <Text style={styles.quantityText}>{quantity}</Text>
                <TouchableOpacity style={styles.quantityButton} onPress={increaseQuantity}>
                  <Ionicons name="add" size={20} color="#6b7280" />
                </TouchableOpacity>
              </View>
            </View>

            {/* Buy Button */}
            <TouchableOpacity style={styles.buyButton} onPress={handleBuyPress}>
              <Ionicons name="logo-paypal" size={24} color="white" />
              <Text style={styles.buyButtonText}>Buy with PayPal</Text>
            </TouchableOpacity>

            <Text style={styles.secureText}>Secure payment powered by PayPal</Text>
          </View>
        </View>
      </View>

      {/* Features Section */}
      <View style={styles.featuresSection}>
        <View style={styles.featureCard}>
          <Ionicons name="rocket" size={48} color="#3b82f6" />
          <Text style={styles.featureCardTitle}>Fast Shipping</Text>
          <Text style={styles.featureCardText}>
            Orders ship within 2-3 business days. Free shipping on orders over $50.
          </Text>
        </View>

        <View style={styles.featureCard}>
          <Ionicons name="refresh" size={48} color="#10b981" />
          <Text style={styles.featureCardTitle}>Easy Returns</Text>
          <Text style={styles.featureCardText}>
            30-day return policy. If you're not satisfied, we'll make it right.
          </Text>
        </View>

        <View style={styles.featureCard}>
          <Ionicons name="heart" size={48} color="#8b5cf6" />
          <Text style={styles.featureCardTitle}>Climate Action</Text>
          <Text style={styles.featureCardText}>
            Every purchase supports climate awareness and activism efforts.
          </Text>
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
  productCard: {
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
  productGrid: {
    flexDirection: 'column',
  },
  imageSection: {
    alignItems: 'center',
    marginBottom: 20,
  },
  productImage: {
    width: width * 0.7,
    height: 300,
    marginBottom: 16,
  },
  viewToggle: {
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
  quantityControls: {
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
  quantityText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    minWidth: 40,
    textAlign: 'center',
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