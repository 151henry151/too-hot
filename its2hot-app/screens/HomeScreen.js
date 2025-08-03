import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
  Dimensions,
  Platform,
  TextInput,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import * as Location from 'expo-location';
import { useLogger, logError } from '../hooks/useLogger';
import { useLoadingState, LOADING_KEYS, LOADING_MESSAGES } from '../hooks/useLoadingState';
import LoadingWrapper, { LoadingOverlay, LoadingButton } from '../components/LoadingWrapper';
import { 
  ACCESSIBILITY, 
  createButtonAccessibility, 
  createTextAccessibility, 
  createInputAccessibility,
  createImageAccessibility,
  createModalAccessibility,
  createAccessibilityProps
} from '../utils/accessibility';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [manualLocation, setManualLocation] = useState('');
  const logger = useLogger();
  const { setLoading, withLoading } = useLoadingState();

  // Check notification permission on mount
  useEffect(() => {
    const checkNotificationStatus = async () => {
      const { status } = await Notifications.getPermissionsAsync();
      setIsSubscribed(status === 'granted');
    };
    checkNotificationStatus();
  }, []);

  const getUserLocation = async () => {
    return await withLoading(LOADING_KEYS.LOCATION_FETCH, async () => {
      logger.info('Requesting location permission', 'Location');
      
      // Request location permission
      setLoading(LOADING_KEYS.LOCATION_PERMISSION, true, LOADING_MESSAGES[LOADING_KEYS.LOCATION_PERMISSION]);
      const { status } = await Location.requestForegroundPermissionsAsync();
      setLoading(LOADING_KEYS.LOCATION_PERMISSION, false);
      
      if (status !== 'granted') {
        logger.warn('Location permission denied', 'Location');
        // Show modal for manual location input instead of alert
        setShowLocationModal(true);
        return null;
      }

      logger.info('Getting current location', 'Location');
      
      // Get current location
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeInterval: 10000,
        distanceInterval: 10,
      });

      logger.info('Location obtained', 'Location', {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy
      });

      // Reverse geocode to get city name
      setLoading(LOADING_KEYS.LOCATION_GEOCODE, true, LOADING_MESSAGES[LOADING_KEYS.LOCATION_GEOCODE]);
      const geocode = await Location.reverseGeocodeAsync({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      setLoading(LOADING_KEYS.LOCATION_GEOCODE, false);

      if (geocode && geocode.length > 0) {
        const place = geocode[0];
        const city = place.city || place.subregion || place.region || 'Unknown';
        const state = place.region || '';
        const locationString = state ? `${city}, ${state}` : city;
        
        logger.info('Location resolved', 'Location', { locationString });
        return locationString;
      } else {
        logger.warn('Could not resolve location name', 'Location');
        return 'Unknown Location';
      }
    }, LOADING_MESSAGES[LOADING_KEYS.LOCATION_FETCH]);
  };

  const handleNotificationSignup = async () => {
    return await withLoading(LOADING_KEYS.NOTIFICATION_SUBSCRIBE, async () => {
      if (!Device.isDevice) {
        const msg = 'Push notifications are only supported on physical devices.';
        logger.error(msg, 'Device check');
        Alert.alert('Error', msg);
        return;
      }

      logger.info('Requesting notification permission', 'Notifications');

      // Request permission
      setLoading(LOADING_KEYS.NOTIFICATION_PERMISSION, true, LOADING_MESSAGES[LOADING_KEYS.NOTIFICATION_PERMISSION]);
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        logger.info('Requesting notification permission', 'Notifications');
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      setLoading(LOADING_KEYS.NOTIFICATION_PERMISSION, false);
      
      if (finalStatus !== 'granted') {
        logger.warn('Notification permission denied', 'Notifications');
        Alert.alert(
          'Permission Required',
          'Please enable notifications in your device settings to receive temperature alerts.',
          [{ text: 'OK' }]
        );
        return;
      }

      logger.info('Notification permission granted', 'Notifications');

      // Get user location
      const location = await getUserLocation();
      
      // Register device with backend (this will get the push token)
      setLoading(LOADING_KEYS.DEVICE_REGISTRATION, true, LOADING_MESSAGES[LOADING_KEYS.DEVICE_REGISTRATION]);
      await registerDeviceWithLocation(location);
      setLoading(LOADING_KEYS.DEVICE_REGISTRATION, false);

      setIsSubscribed(true);
      logger.info('Successfully subscribed to notifications', 'Notifications');
      
      Alert.alert(
        'Success!',
        'You\'re now subscribed to temperature alerts. You\'ll receive notifications when temperatures are 10°F+ hotter than average in your area.',
        [{ text: 'OK' }]
      );
    }, LOADING_MESSAGES[LOADING_KEYS.NOTIFICATION_SUBSCRIBE]);
  };

  const handleNotificationDisable = async () => {
    return await withLoading(LOADING_KEYS.NOTIFICATION_UNSUBSCRIBE, async () => {
      logger.info('Disabling notifications', 'Notifications');
      
      // Unregister from backend
      const response = await fetch('https://its2hot.org/api/unregister-device', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform: Platform.OS,
          device_type: Platform.OS === 'ios' ? 'ios' : 'android',
        }),
      });

      if (response.ok) {
        logger.info('Successfully unregistered device', 'Notifications');
        setIsSubscribed(false);
        Alert.alert('Success', 'You\'ve been unsubscribed from temperature alerts.');
      } else {
        logger.error('Failed to unregister device', 'Notifications');
        Alert.alert('Error', 'Failed to unsubscribe. Please try again.');
      }
    }, LOADING_MESSAGES[LOADING_KEYS.NOTIFICATION_UNSUBSCRIBE]);
  };

  const handleShopPress = () => {
    logger.info('Navigating to shop', 'Navigation');
    navigation.navigate('Shop');
  };

  const handleManualLocationSubmit = async () => {
    if (!manualLocation.trim()) {
      Alert.alert('Error', 'Please enter a location.');
      return;
    }

    return await withLoading(LOADING_KEYS.DEVICE_REGISTRATION, async () => {
      await registerDeviceWithLocation(manualLocation.trim());
      setShowLocationModal(false);
      setManualLocation('');
      Alert.alert('Success', `Location set to ${manualLocation.trim()}`);
    }, 'Setting location...');
  };

  const registerDeviceWithLocation = async (location) => {
    try {
      // Get the push token first
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: 'cd9501a1-6d26-4451-ab0a-54631514d4fe',
      });

      const response = await fetch('https://its2hot.org/api/register-device', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          push_token: token.data,
          platform: 'expo',
          device_type: Platform.OS === 'ios' ? 'ios' : 'android',
          location: location,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to register device');
      }

      logger.info('Device registered successfully', 'Device Registration', { location, token: token.data });
    } catch (error) {
      logger.error('Device registration error: ' + (error?.toString?.() || String(error)), 'Device Registration');
      throw error;
    }
  };

  return (
    <LoadingOverlay
      loadingKey={LOADING_KEYS.LOCATION_FETCH}
      loadingMessage={LOADING_MESSAGES[LOADING_KEYS.LOCATION_FETCH]}
    >
      <ScrollView 
        style={styles.container}
        contentContainerStyle={styles.contentContainer}
        {...createAccessibilityProps(
          'Home screen with temperature alert subscription options',
          'Scroll to view all content on the home screen'
        )}
      >
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <Text 
          style={styles.heroTitle}
          {...createTextAccessibility('IT\'S TOO HOT! - Temperature Alert App', ACCESSIBILITY.ROLES.HEADER)}
        >
          IT'S TOO HOT!
        </Text>
        <Text 
          style={styles.heroSubtitle}
          {...createTextAccessibility('Get notified when temperatures are 10 degrees Fahrenheit or more above average in your area')}
        >
          Get notified when temperatures are 10°F+ above average
        </Text>
      </View>

      {/* Campaign Info */}
      <View style={styles.campaignSection}>
        <Text 
          style={styles.campaignTitle}
          {...createTextAccessibility('Campaign Information', ACCESSIBILITY.ROLES.HEADER)}
        >
          Climate Awareness Campaign
        </Text>
        <Text 
          style={styles.campaignText}
          {...createTextAccessibility('This campaign raises awareness about climate change by alerting people when temperatures are significantly above historical averages')}
        >
          This campaign raises awareness about climate change by alerting people when temperatures are significantly above historical averages.
        </Text>
      </View>

      {/* Temperature Alert Section */}
      <View style={styles.alertSection}>
        <Text 
          style={styles.alertTitle}
          {...createTextAccessibility('Temperature Alert Subscription', ACCESSIBILITY.ROLES.HEADER)}
        >
          Get Temperature Alerts
        </Text>
        <Text 
          style={styles.alertText}
          {...createTextAccessibility('Subscribe to receive notifications when temperatures in your area are 10 degrees Fahrenheit or more above the 30-year average')}
        >
          Subscribe to receive notifications when temperatures in your area are 10°F+ above the 30-year average.
        </Text>
        
        {isSubscribed ? (
          <LoadingButton
            loadingKey={LOADING_KEYS.NOTIFICATION_UNSUBSCRIBE}
            onPress={handleNotificationDisable}
          >
            <TouchableOpacity
              style={[styles.button, styles.unsubscribeButton]}
              {...createButtonAccessibility(
                ACCESSIBILITY.LABELS.UNSUBSCRIBE_BUTTON,
                ACCESSIBILITY.HINTS.UNSUBSCRIBE_BUTTON,
                false
              )}
            >
              <Ionicons name="notifications-off" size={20} color="white" />
              <Text style={styles.buttonText}>
                Unsubscribe from Alerts
              </Text>
            </TouchableOpacity>
          </LoadingButton>
        ) : (
          <LoadingButton
            loadingKey={LOADING_KEYS.NOTIFICATION_SUBSCRIBE}
            onPress={handleNotificationSignup}
          >
            <TouchableOpacity
              style={[styles.button, styles.subscribeButton]}
              {...createButtonAccessibility(
                ACCESSIBILITY.LABELS.SUBSCRIBE_BUTTON,
                ACCESSIBILITY.HINTS.SUBSCRIBE_BUTTON,
                false
              )}
            >
              <Ionicons name="notifications" size={20} color="white" />
              <Text style={styles.buttonText}>
                Subscribe to Alerts
              </Text>
            </TouchableOpacity>
          </LoadingButton>
        )}
      </View>

      {/* Features Section */}
      <View style={styles.featuresSection}>
        <Text 
          style={styles.featuresTitle}
          {...createTextAccessibility('Campaign Features', ACCESSIBILITY.ROLES.HEADER)}
        >
          Why This Matters
        </Text>
        <View style={styles.featuresGrid}>
          <View style={styles.feature}>
            <Ionicons name="eye" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Visual Impact - Makes climate change visible and tangible')}
            >
              Visual Impact
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Makes climate change visible and tangible')}
            >
              Makes climate change visible and tangible
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="chatbubbles" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Conversation Starter - Starts important climate discussions')}
            >
              Conversation Starter
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Starts important climate discussions')}
            >
              Starts important climate discussions
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="people" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Community Unity - Brings people together around climate action')}
            >
              Community Unity
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Brings people together around climate action')}
            >
              Brings people together around climate action
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="analytics" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Data-Driven - Based on actual temperature data and historical averages')}
            >
              Data-Driven
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Based on actual temperature data and historical averages')}
            >
              Based on actual temperature data and historical averages
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="megaphone" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Community Action - Encourages local climate action and awareness')}
            >
              Community Action
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Encourages local climate action and awareness')}
            >
              Encourages local climate action and awareness
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="trending-up" size={24} color="black" />
            <Text 
              style={styles.featureTitle}
              {...createTextAccessibility('Raise Awareness - Helps people understand the impact of climate change')}
            >
              Raise Awareness
            </Text>
            <Text 
              style={styles.featureText}
              {...createTextAccessibility('Helps people understand the impact of climate change')}
            >
              Helps people understand the impact of climate change
            </Text>
          </View>
        </View>
      </View>

      {/* Get Your Shirt Section */}
      <View style={styles.shirtSection}>
        <Text 
          style={styles.shirtTitle}
          {...createTextAccessibility('Get Your Shirt', ACCESSIBILITY.ROLES.HEADER)}
        >
          Get Your "IT'S TOO HOT!" Shirt
        </Text>
        <Text 
          style={styles.shirtText}
          {...createTextAccessibility('Wear the shirt when you get the alert to raise climate awareness')}
        >
          Wear the shirt when you get the alert to raise climate awareness.
        </Text>
        <Image
          source={require('../assets/images/tshirt.png')}
          style={styles.shirtImage}
          {...createImageAccessibility('IT\'S TOO HOT! t-shirt design preview')}
        />
        <TouchableOpacity
          style={styles.shopButton}
          onPress={handleShopPress}
          {...createButtonAccessibility(
            ACCESSIBILITY.LABELS.SHOP_BUTTON,
            ACCESSIBILITY.HINTS.SHOP_BUTTON
          )}
        >
          <Text style={styles.shopButtonText}>Get Your Shirt</Text>
          <Ionicons name="arrow-forward" size={20} color="white" />
        </TouchableOpacity>
      </View>

      {/* Location Modal */}
      <Modal
        visible={showLocationModal}
        transparent={true}
        animationType="slide"
        {...createModalAccessibility(
          'Location Input',
          'Enter your city or location name for accurate temperature alerts'
        )}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text 
              style={styles.modalTitle}
              {...createTextAccessibility('Set Your Location', ACCESSIBILITY.ROLES.HEADER)}
            >
              Set Your Location
            </Text>
            <Text 
              style={styles.modalText}
              {...createTextAccessibility('Enter your city or location name to receive accurate temperature alerts for your area')}
            >
              Enter your city or location name to receive accurate temperature alerts for your area.
            </Text>
            <TextInput
              style={styles.locationInput}
              value={manualLocation}
              onChangeText={setManualLocation}
              placeholder="Enter your city (e.g., New York, NY)"
              placeholderTextColor="#666"
              {...createInputAccessibility(
                ACCESSIBILITY.LABELS.MANUAL_LOCATION_INPUT,
                ACCESSIBILITY.HINTS.MANUAL_LOCATION_INPUT,
                true
              )}
            />
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowLocationModal(false)}
                {...createButtonAccessibility(
                  ACCESSIBILITY.LABELS.CANCEL,
                  'Double tap to cancel location input'
                )}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.submitButton]}
                onPress={handleManualLocationSubmit}
                {...createButtonAccessibility(
                  ACCESSIBILITY.LABELS.MANUAL_LOCATION_SUBMIT,
                  ACCESSIBILITY.HINTS.MANUAL_LOCATION_SUBMIT
                )}
              >
                <Text style={styles.submitButtonText}>Submit</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
    </LoadingOverlay>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  contentContainer: {
    paddingBottom: 20, // Add some padding at the bottom for the modal
  },
  heroSection: {
    backgroundColor: '#1a1a1a',
    paddingVertical: 40,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#d1d5db',
    textAlign: 'center',
    lineHeight: 24,
  },
  campaignSection: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 24,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    alignItems: 'center',
  },
  campaignTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  campaignText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  alertSection: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 24,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    alignItems: 'center',
  },
  alertTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  alertText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  subscribeButton: {
    backgroundColor: '#3b82f6',
  },
  unsubscribeButton: {
    backgroundColor: '#ef4444',
  },
  buttonDisabled: {
    backgroundColor: '#10b981',
  },
  buttonLoading: {
    backgroundColor: '#6b7280',
    opacity: 0.7,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    marginLeft: 8,
  },
  shirtSection: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 24,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    alignItems: 'center',
  },
  shirtTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
  },
  shirtText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  shirtImage: {
    width: width * 0.6,
    height: 200,
    marginBottom: 20,
  },
  shopButton: {
    backgroundColor: 'black',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'white',
  },
  shopButtonText: {
    color: 'white',
    fontWeight: 'bold',
    marginRight: 8,
  },
  featuresSection: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 24,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    alignItems: 'center',
  },
  featuresTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  feature: {
    width: '48%', // Adjust for two columns
    alignItems: 'center',
    marginBottom: 16,
    minWidth: 120,
  },
  featureTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 8,
    marginBottom: 4,
    textAlign: 'center',
  },
  featureText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 16,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
  },
  locationText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 6,
    fontWeight: '500',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    marginHorizontal: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  modalIcon: {
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  modalText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  locationInput: {
    width: '100%',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#f9fafb',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  cancelButton: {
    backgroundColor: '#f3f4f6',
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  submitButton: {
    backgroundColor: '#3b82f6',
  },
  cancelButtonText: {
    color: '#6b7280',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '500',
  },
  submitButtonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '500',
  },
}); 