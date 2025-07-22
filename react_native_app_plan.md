# IT'S TOO HOT! React Native App Building Plan

## 1. Set Up Your React Native Project
- Use Expo for the fastest start (recommended)
- Install Expo CLI: `npm install -g expo-cli`
- Create project: `expo init its2hot-app`
- Enter project: `cd its2hot-app`
- Install notifications dependencies: `expo install expo-notifications expo-device`

## 2. Set Up Firebase Project
- Go to [Firebase Console](https://console.firebase.google.com/)
- Create a new project (e.g., "Its2Hot")
- Add Android and iOS apps to the project
- Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)

## 3. Integrate FCM with Expo
- Follow [Expo Push Notifications guide](https://docs.expo.dev/push-notifications/overview/)
- For bare React Native, use [@react-native-firebase/messaging](https://rnfirebase.io/messaging/usage)
- Configure FCM for both platforms

## 4. Implement Notification Registration and Handling
- Register device for push notifications
- Store Expo push token (or FCM token) in your backend
- Use Expo or Firebase API to send notifications

## 5. Build the Core App UI
- Home screen: "Get The Alert", "Wear The Shirt", etc.
- Shop screen: Link to t-shirt shop
- Settings: Manage notification preferences
- Notification handling: Show alerts when received

## 6. Prepare for App Store/Play Store
- Configure app icons, splash screens, and store metadata
- For Expo: configure `app.json`/`app.config.js`
- Build with `eas build` for iOS and Android
- Submit to the Apple App Store and Google Play Store

---

**Optional:**
- Add analytics, deep linking, or advanced notification features
- Build a backend endpoint for storing and managing push tokens
- Add climate alert logic to trigger notifications 