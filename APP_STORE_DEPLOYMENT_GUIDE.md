# App Store Deployment Guide

## Prerequisites

1. **Node.js Setup**: Use NVM to manage Node.js versions
   ```bash
   # Install NVM if not already installed
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   
   # Load NVM and install Node.js 18
   export NVM_DIR="$HOME/.nvm"
   [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
   nvm install 18
   nvm use 18
   ```

2. **EAS CLI Installation**:
   ```bash
   npm install -g eas-cli
   ```

3. **Expo Authentication**:
   ```bash
   eas login
   # Login as: romp
   ```

4. **Apple Developer Account**: Ensure you have access to Apple Developer account (151henry151@gmail.com)

## Build and Upload Process

### Step 1: Build the iOS App

```bash
# Navigate to the app directory
cd its2hot-app

# Build for production (non-interactive mode to avoid prompts)
export EAS_BUILD_TIMEOUT=1200
eas build --platform ios --profile production --non-interactive
```

**Expected Output:**
```
✔ Incremented buildNumber from X to Y
✔ Using remote iOS credentials (Expo server)
✔ Build finished
🍏 iOS app: https://expo.dev/artifacts/eas/[BUILD_ID].ipa
```

### Step 2: Download the IPA File

```bash
# Download the built IPA file
curl -L -o its2hot-app-v[VERSION].ipa "https://expo.dev/artifacts/eas/[BUILD_ID].ipa" --progress-bar
```

**Example:**
```bash
curl -L -o its2hot-app-v11.ipa "https://expo.dev/artifacts/eas/5CTLh99oQZDMDxz122R5yG.ipa" --progress-bar
```

### Step 3: Upload to App Store Connect

```bash
# Upload using xcrun altool
xcrun altool --upload-app -f its2hot-app-v[VERSION].ipa -t ios -u 151henry151@gmail.com
```

**Expected Output:**
```
UPLOAD SUCCEEDED with 0 warnings, 0 messages
Delivery UUID: [UUID]
Transferred [SIZE] bytes in [TIME] seconds ([SPEED])
```

## Troubleshooting

### SSL Errors During Build
If you encounter SSL errors during the build upload:
```bash
# Set a longer timeout and retry
export EAS_BUILD_TIMEOUT=1200
eas build --platform ios --profile production --non-interactive
```

### Build Version Conflicts
If you get "bundle version must be higher" error:
- The build was already uploaded successfully
- Check App Store Connect for the build
- Increment build number for next upload

### Missing Push Token Issue
If push notifications aren't working:
1. Ensure the mobile app sends `push_token` in the registration request
2. Check that `registerDeviceWithLocation` function includes the token
3. Verify backend expects `push_token` field

## Configuration Files

### EAS Configuration (`eas.json`)
```json
{
  "cli": {
    "version": ">= 16.17.0",
    "appVersionSource": "remote"
  },
  "build": {
    "production": {
      "autoIncrement": true,
      "ios": {
        "resourceClass": "m-medium",
        "buildConfiguration": "Release",
        "distribution": "store"
      }
    }
  }
}
```

### App Configuration (`app.json`)
Key iOS settings:
```json
{
  "ios": {
    "bundleIdentifier": "com.romp.its2hot",
    "infoPlist": {
      "NSCameraUsageDescription": "This app may access the camera for enhanced user experience features.",
      "UIBackgroundModes": ["remote-notification"]
    }
  }
}
```

## Verification Steps

1. **Check App Store Connect**: https://appstoreconnect.apple.com
2. **Look for Build**: Version 1.0.0, Build [NUMBER]
3. **Wait for Processing**: Can take 10-30 minutes
4. **TestFlight**: Build should appear in TestFlight for testing

## Common Issues and Solutions

### Issue: "Missing purpose string in Info.plist"
**Solution**: Add required privacy descriptions to `app.json`:
```json
"NSCameraUsageDescription": "This app may access the camera for enhanced user experience features."
```

### Issue: Push notifications not working
**Solution**: Ensure mobile app sends push token:
```javascript
body: JSON.stringify({
  push_token: token.data,
  platform: 'expo',
  device_type: Platform.OS === 'ios' ? 'ios' : 'android',
  location: location,
})
```

### Issue: Build not appearing in App Store Connect
**Solution**: 
1. Wait for processing (10-30 minutes)
2. Check email for processing completion
3. Verify upload was successful with UUID

## Environment Variables

Required environment variables:
- `EAS_BUILD_TIMEOUT`: Set to 1200 for longer builds
- Apple ID credentials (handled by EAS)

## Notes

- Build numbers auto-increment with EAS
- Each build must have a unique version number
- Processing time varies (10-30 minutes)
- TestFlight builds appear before App Store builds
- Always test push notifications in TestFlight before App Store submission 