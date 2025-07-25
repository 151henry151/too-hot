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
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { useLogger, logError } from '../hooks/useLogger';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const logger = useLogger();

  // Check notification permission on mount
  useEffect(() => {
    const checkNotificationStatus = async () => {
      const { status } = await Notifications.getPermissionsAsync();
      setIsSubscribed(status === 'granted');
    };
    checkNotificationStatus();
  }, []);

  const handleNotificationSignup = async () => {
    setIsLoading(true);
    try {
      if (!Device.isDevice) {
        const msg = 'Push notifications are only supported on physical devices.';
        logger.error(msg, 'Device check');
        Alert.alert('Error', msg);
        setIsLoading(false);
        return;
      }
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      logger.info('Existing notification permission status: ' + existingStatus, 'Permissions');
      let finalStatus = existingStatus;
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
        logger.info('Requested notification permission status: ' + finalStatus, 'Permissions');
      }
      if (finalStatus !== 'granted') {
        const msg = 'To receive temperature alerts, please enable notifications in your device settings.';
        logger.warn(msg, 'Permission not granted');
        Alert.alert('Permission Required', msg, [
          { text: 'Cancel' },
          { text: 'Open Settings', onPress: () => { Alert.alert('Settings', 'Please go to your device settings and enable notifications for this app.'); }}
        ]);
        setIsLoading(false);
        return;
      }
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      logger.info('Push token: ' + token, 'Push Token');
      
      // Get user's location (you can implement geolocation here)
      // For now, we'll use a default location or get it from user input
      const userLocation = 'auto'; // This should be replaced with actual location detection
      
      // Use production API endpoint for device registration
      const response = await fetch('https://its2hot.org/api/register-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          push_token: token, 
          platform: 'expo', 
          device_type: Platform.OS,
          location: userLocation
        })
      });
      if (response.ok) {
        setIsSubscribed(true);
        logger.log('Device registered for push notifications', 'Register Device', { token });
        Alert.alert('Success!', 'You will now receive alerts when temperatures are 10°F+ hotter than average.', [{ text: 'OK' }]);
      } else {
        const errorData = await response.json();
        const msg = errorData.error || 'Failed to register device. Please try again.';
        logger.error('Backend error: ' + msg, 'Backend response');
        Alert.alert('Error', msg);
      }
    } catch (error) {
      logger.error('Notification setup error: ' + (error?.toString?.() || String(error)), 'Exception');
      Alert.alert('Error', 'Failed to set up notifications. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNotificationDisable = async () => {
    setIsLoading(true);
    try {
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      logger.info('Attempting to unregister device for push notifications', 'Unregister Device', { token });
      const response = await fetch('https://its2hot.org/api/unregister-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ push_token: token })
      });
      if (response.ok) {
        setIsSubscribed(false);
        logger.log('Device unregistered for push notifications', 'Unregister Device', { token });
        Alert.alert('Notifications Disabled', 'You will no longer receive alerts.');
      } else {
        const errorData = await response.json();
        const msg = errorData.error || 'Failed to disable notifications. Please try again.';
        logger.error('Backend error: ' + msg, 'Backend response');
        Alert.alert('Error', msg);
      }
    } catch (error) {
      logger.error('Notification disable error: ' + (error?.toString?.() || String(error)), 'Exception');
      Alert.alert('Error', 'Failed to disable notifications. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleShopPress = () => {
    navigation.navigate('Shop');
  };

  return (
    <ScrollView style={styles.container}>
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <View style={styles.heroContent}>
          <Ionicons name="thermometer" size={48} color="#3b82f6" />
          <Text style={styles.heroTitle}>Climate Action Starts Here</Text>
          <Text style={styles.heroSubtitle}>
            Join the movement to raise awareness about climate change
          </Text>
        </View>
      </View>

      {/* Get The Alert Section */}
      <View style={styles.card}>
        <Ionicons name="phone-portrait" size={48} color="#8b5cf6" />
        <Text style={styles.cardTitle}>Get The Alert</Text>
        <Text style={styles.cardDescription}>
          Get an alert when temperatures are 10°F hotter than average
        </Text>
        
        <TouchableOpacity
          style={[styles.button, isSubscribed && styles.buttonDisabled, isLoading && styles.buttonLoading]}
          onPress={handleNotificationSignup}
          disabled={isSubscribed || isLoading}
        >
          {isLoading ? (
            <>
              <Ionicons name="hourglass" size={20} color="white" />
              <Text style={styles.buttonText}>Setting up...</Text>
            </>
          ) : (
            <>
              <Ionicons 
                name={isSubscribed ? "checkmark-circle" : "notifications"} 
                size={20} 
                color="white" 
              />
              <Text style={styles.buttonText}>
                {isSubscribed ? 'Notifications Enabled' : 'Enable Notifications'}
              </Text>
            </>
          )}
        </TouchableOpacity>

        {isSubscribed && !isLoading && (
          <TouchableOpacity
            style={[styles.button, { backgroundColor: '#ef4444', marginTop: 8 }]}
            onPress={handleNotificationDisable}
          >
            <Ionicons name="notifications-off" size={20} color="white" />
            <Text style={styles.buttonText}>Disable Notifications</Text>
          </TouchableOpacity>
        )}

        {/* Shirt Section */}
        <View style={styles.shirtSection}>
          <Ionicons name="shirt" size={48} color="#3b82f6" />
          <Text style={styles.shirtTitle}>Wear The Shirt</Text>
          <Text style={styles.shirtDescription}>
            Wear your "IT'S TOO HOT!" shirt
          </Text>
          <TouchableOpacity style={styles.shopButton} onPress={handleShopPress}>
            <Ionicons name="shirt" size={20} color="white" />
            <Text style={styles.buttonText}>Get The Shirt</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Climate Data Tracking */}
      <View style={styles.card}>
        <Ionicons name="analytics" size={48} color="#3b82f6" />
        <Text style={styles.cardTitle}>Climate Data Tracking</Text>
        <Text style={styles.cardDescription}>
          We monitor real-time temperature data and compare it to historical averages to identify when temperatures are 10°F+ hotter than normal.
        </Text>
      </View>

      {/* Action Alerts */}
      <View style={styles.card}>
        <Ionicons name="mail" size={48} color="#10b981" />
        <Text style={styles.cardTitle}>Action Alerts</Text>
        <Text style={styles.cardDescription}>
          Get notified when temperatures are 10°F+ hotter than average so you can take action and raise awareness.
        </Text>
      </View>

      {/* T-Shirt Design Section */}
      <View style={styles.tshirtCard}>
        <Text style={styles.tshirtCardTitle}>THE "IT'S TOO HOT!" SHIRT</Text>
        <View style={styles.tshirtImageContainer}>
          <Image
            source={require('../assets/images/tshirt.png')}
            style={styles.tshirtImage}
            resizeMode="contain"
          />
        </View>
        <Text style={styles.tshirtDescription}>
          Wear this shirt on days when temperatures are 10°F+ hotter than the historical average for that day to raise awareness about climate change.
        </Text>
        
        <View style={styles.featuresGrid}>
          <View style={styles.feature}>
            <Ionicons name="eye" size={24} color="black" />
            <Text style={styles.featureTitle}>Visual Impact</Text>
            <Text style={styles.featureText}>Bold, clean design that gets attention</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="chatbubbles" size={24} color="black" />
            <Text style={styles.featureTitle}>Conversation Starter</Text>
            <Text style={styles.featureText}>Starts important climate discussions</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="people" size={24} color="black" />
            <Text style={styles.featureTitle}>Community Unity</Text>
            <Text style={styles.featureText}>Shows solidarity with climate activists</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.getShirtButton} onPress={handleShopPress}>
          <Ionicons name="cart" size={20} color="white" />
          <Text style={styles.buttonText}>GET YOUR SHIRT</Text>
        </TouchableOpacity>
      </View>

      {/* Why This Matters */}
      <View style={styles.card}>
        <Ionicons name="globe" size={48} color="#3b82f6" />
        <Text style={styles.cardTitle}>WHY THIS MATTERS</Text>
        <Text style={styles.cardDescription}>
          Climate change is happening faster than predicted. When temperatures are 10°F+ hotter than the historical average for that day, it's a clear sign of climate disruption. Wearing your "IT'S TOO HOT!" shirt on these days helps raise awareness and start conversations about climate action.
        </Text>
        
        <View style={styles.featuresGrid}>
          <View style={styles.feature}>
            <Ionicons name="trending-up" size={24} color="#3b82f6" />
            <Text style={styles.featureTitle}>Data-Driven</Text>
            <Text style={styles.featureText}>Real climate data, not just weather</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="people" size={24} color="#10b981" />
            <Text style={styles.featureTitle}>Community Action</Text>
            <Text style={styles.featureText}>Join thousands of climate activists</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="megaphone" size={24} color="#ef4444" />
            <Text style={styles.featureTitle}>Raise Awareness</Text>
            <Text style={styles.featureText}>Start conversations about climate change</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  heroSection: {
    backgroundColor: '#1a1a1a',
    paddingVertical: 40,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  heroContent: {
    alignItems: 'center',
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
  card: {
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
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  cardDescription: {
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
    alignItems: 'center',
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  shirtTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
  },
  shirtDescription: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  shopButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  tshirtCard: {
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
    borderWidth: 2,
    borderColor: 'black',
  },
  tshirtCardTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 20,
    textAlign: 'center',
  },
  tshirtImageContainer: {
    marginBottom: 20,
  },
  tshirtImage: {
    width: width * 0.6,
    height: 200,
  },
  tshirtDescription: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  feature: {
    width: '30%',
    alignItems: 'center',
    marginBottom: 16,
  },
  featureTitle: {
    fontSize: 14,
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
  getShirtButton: {
    backgroundColor: 'black',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'white',
  },
}); 