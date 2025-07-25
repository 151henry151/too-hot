import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import * as Notifications from 'expo-notifications';

// Import screens
import HomeScreen from './screens/HomeScreen';
import ShopScreen from './screens/ShopScreen';
import TooHotTodayScreen from './screens/TooHotTodayScreen';

const Stack = createStackNavigator();

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export default function App() {
  const navigationRef = React.useRef();
  useEffect(() => {
    // Set up notification listeners when app starts
    const foregroundSubscription = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received in foreground:', notification);
    });

    const responseSubscription = Notifications.addNotificationResponseReceivedListener(response => {
      console.log('Notification response received:', response);
      // Navigate to TooHotTodayScreen with data if present
      const data = response?.notification?.request?.content?.data;
      if (data && navigationRef.current) {
        navigationRef.current.navigate('TooHotToday', {
          location: data.location,
          current_temp: data.current_temp,
          avg_temp: data.avg_temp,
        });
      }
    });

    return () => {
      foregroundSubscription.remove();
      responseSubscription.remove();
    };
  }, []);

  return (
    <NavigationContainer ref={navigationRef}>
      <StatusBar style="light" />
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1a1a1a',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{
            title: 'TOO HOT',
            headerRight: () => null,
          }}
        />
        <Stack.Screen 
          name="Shop" 
          component={ShopScreen}
          options={{
            title: 'Shop',
          }}
        />
        <Stack.Screen
          name="TooHotToday"
          component={TooHotTodayScreen}
          options={{
            title: 'Too Hot Today',
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
} 