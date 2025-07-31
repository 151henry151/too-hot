import * as Updates from 'expo-updates';
import { Alert, Platform } from 'react-native';
import { useLogger } from '../hooks/useLogger';

class UpdateService {
  constructor() {
    this.logger = useLogger();
    this.isCheckingForUpdates = false;
    this.updateAvailable = false;
    this.updateDownloaded = false;
  }

  /**
   * Check for available updates
   * @returns {Promise<boolean>} True if update is available
   */
  async checkForUpdates() {
    try {
      this.logger.info('Checking for updates', 'UpdateService');
      
      if (this.isCheckingForUpdates) {
        this.logger.info('Update check already in progress', 'UpdateService');
        return false;
      }

      this.isCheckingForUpdates = true;

      // Check if updates are enabled
      if (!Updates.isEnabled) {
        this.logger.warn('Updates are disabled', 'UpdateService');
        return false;
      }

      // Check for available update
      const update = await Updates.checkForUpdateAsync();
      
      if (update.isAvailable) {
        this.logger.info('Update available', 'UpdateService', {
          manifest: update.manifest,
          isRollback: update.isRollback
        });
        
        this.updateAvailable = true;
        return true;
      } else {
        this.logger.info('No update available', 'UpdateService');
        this.updateAvailable = false;
        return false;
      }
    } catch (error) {
      this.logger.error('Error checking for updates: ' + (error?.toString?.() || String(error)), 'UpdateService');
      return false;
    } finally {
      this.isCheckingForUpdates = false;
    }
  }

  /**
   * Download and apply the update
   * @returns {Promise<boolean>} True if update was successful
   */
  async downloadAndApplyUpdate() {
    try {
      this.logger.info('Starting update download', 'UpdateService');
      
      if (!this.updateAvailable) {
        this.logger.warn('No update available to download', 'UpdateService');
        return false;
      }

      // Show loading alert
      Alert.alert(
        'Updating App',
        'Downloading the latest version...',
        [{ text: 'OK' }],
        { cancelable: false }
      );

      // Download the update
      const result = await Updates.fetchUpdateAsync();
      
      if (result.isNew) {
        this.logger.info('Update downloaded successfully', 'UpdateService', {
          manifest: result.manifest
        });
        
        this.updateDownloaded = true;
        
        // Show success message
        Alert.alert(
          'Update Ready',
          'The update has been downloaded. The app will restart to apply the changes.',
          [
            {
              text: 'Restart Now',
              onPress: () => this.applyUpdate()
            },
            {
              text: 'Later',
              style: 'cancel'
            }
          ]
        );
        
        return true;
      } else {
        this.logger.info('No new update to download', 'UpdateService');
        return false;
      }
    } catch (error) {
      this.logger.error('Error downloading update: ' + (error?.toString?.() || String(error)), 'UpdateService');
      
      Alert.alert(
        'Update Failed',
        'Failed to download the update. Please try again later.',
        [{ text: 'OK' }]
      );
      
      return false;
    }
  }

  /**
   * Apply the downloaded update
   */
  async applyUpdate() {
    try {
      this.logger.info('Applying update', 'UpdateService');
      
      // Reload the app to apply the update
      await Updates.reloadAsync();
    } catch (error) {
      this.logger.error('Error applying update: ' + (error?.toString?.() || String(error)), 'UpdateService');
      
      Alert.alert(
        'Update Error',
        'Failed to apply the update. Please restart the app manually.',
        [{ text: 'OK' }]
      );
    }
  }

  /**
   * Check for updates on app startup
   */
  async checkForUpdatesOnStartup() {
    try {
      this.logger.info('Checking for updates on startup', 'UpdateService');
      
      // Check if this is a fresh install or update
      const update = await Updates.checkForUpdateAsync();
      
      if (update.isAvailable) {
        this.logger.info('Update available on startup', 'UpdateService');
        
        // For critical updates, show immediate notification
        if (this.isCriticalUpdate(update.manifest)) {
          this.showCriticalUpdateAlert();
        } else {
          // For regular updates, download in background
          this.downloadUpdateInBackground();
        }
      }
    } catch (error) {
      this.logger.error('Error checking for updates on startup: ' + (error?.toString?.() || String(error)), 'UpdateService');
    }
  }

  /**
   * Download update in background without user interaction
   */
  async downloadUpdateInBackground() {
    try {
      this.logger.info('Downloading update in background', 'UpdateService');
      
      const result = await Updates.fetchUpdateAsync();
      
      if (result.isNew) {
        this.logger.info('Background update downloaded', 'UpdateService');
        this.updateDownloaded = true;
        
        // Show notification that update is ready
        this.showUpdateReadyNotification();
      }
    } catch (error) {
      this.logger.error('Error downloading background update: ' + (error?.toString?.() || String(error)), 'UpdateService');
    }
  }

  /**
   * Check if update is critical (security, major bug fixes)
   * @param {Object} manifest - Update manifest
   * @returns {boolean} True if critical update
   */
  isCriticalUpdate(manifest) {
    if (!manifest || !manifest.extra) {
      return false;
    }
    
    // Check for critical update flags
    const extra = manifest.extra;
    return extra.critical || extra.security || extra.urgent;
  }

  /**
   * Show critical update alert
   */
  showCriticalUpdateAlert() {
    Alert.alert(
      'Important Update Available',
      'A critical update is available for your app. This update includes important security improvements and bug fixes.',
      [
        {
          text: 'Update Now',
          onPress: () => this.downloadAndApplyUpdate()
        },
        {
          text: 'Later',
          style: 'cancel'
        }
      ]
    );
  }

  /**
   * Show notification that update is ready
   */
  showUpdateReadyNotification() {
    Alert.alert(
      'Update Ready',
      'A new version of the app is ready to install. Would you like to update now?',
      [
        {
          text: 'Update Now',
          onPress: () => this.applyUpdate()
        },
        {
          text: 'Later',
          style: 'cancel'
        }
      ]
    );
  }

  /**
   * Get current update status
   * @returns {Object} Update status information
   */
  getUpdateStatus() {
    return {
      isEnabled: Updates.isEnabled,
      isAvailable: this.updateAvailable,
      isDownloaded: this.updateDownloaded,
      isChecking: this.isCheckingForUpdates,
      runtimeVersion: Updates.runtimeVersion,
      channel: Updates.channel,
      createdAt: Updates.createdAt,
      updatedAt: Updates.updatedAt
    };
  }

  /**
   * Get update information for debugging
   * @returns {Object} Update information
   */
  async getUpdateInfo() {
    try {
      const update = await Updates.checkForUpdateAsync();
      const status = this.getUpdateStatus();
      
      return {
        ...status,
        updateAvailable: update.isAvailable,
        isRollback: update.isRollback,
        manifest: update.manifest
      };
    } catch (error) {
      this.logger.error('Error getting update info: ' + (error?.toString?.() || String(error)), 'UpdateService');
      return this.getUpdateStatus();
    }
  }

  /**
   * Force check for updates (for manual refresh)
   */
  async forceCheckForUpdates() {
    try {
      this.logger.info('Force checking for updates', 'UpdateService');
      
      const hasUpdate = await this.checkForUpdates();
      
      if (hasUpdate) {
        Alert.alert(
          'Update Available',
          'A new version of the app is available. Would you like to download it now?',
          [
            {
              text: 'Download',
              onPress: () => this.downloadAndApplyUpdate()
            },
            {
              text: 'Cancel',
              style: 'cancel'
            }
          ]
        );
      } else {
        Alert.alert(
          'No Updates',
          'You have the latest version of the app.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      this.logger.error('Error force checking updates: ' + (error?.toString?.() || String(error)), 'UpdateService');
      
      Alert.alert(
        'Update Check Failed',
        'Failed to check for updates. Please try again later.',
        [{ text: 'OK' }]
      );
    }
  }

  /**
   * Initialize update service
   */
  async initialize() {
    try {
      this.logger.info('Initializing update service', 'UpdateService');
      
      // Check for updates on startup
      await this.checkForUpdatesOnStartup();
      
      // Set up periodic update checks (every 24 hours)
      this.schedulePeriodicUpdateCheck();
      
    } catch (error) {
      this.logger.error('Error initializing update service: ' + (error?.toString?.() || String(error)), 'UpdateService');
    }
  }

  /**
   * Schedule periodic update checks
   */
  schedulePeriodicUpdateCheck() {
    // Check for updates every 24 hours
    const UPDATE_CHECK_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours
    
    setInterval(async () => {
      try {
        this.logger.info('Running periodic update check', 'UpdateService');
        await this.checkForUpdates();
      } catch (error) {
        this.logger.error('Error in periodic update check: ' + (error?.toString?.() || String(error)), 'UpdateService');
      }
    }, UPDATE_CHECK_INTERVAL);
  }
}

// Create singleton instance
const updateService = new UpdateService();

export default updateService; 