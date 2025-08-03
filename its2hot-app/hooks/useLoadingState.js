import { useState, useCallback } from 'react';
import { useLogger } from './useLogger';

/**
 * Custom hook for managing loading states
 * Provides comprehensive loading state management with progress tracking
 */
export const useLoadingState = (initialState = {}) => {
  const [loadingStates, setLoadingStates] = useState(initialState);
  const [progress, setProgress] = useState({});
  const logger = useLogger();

  /**
   * Set loading state for a specific key
   * @param {string} key - Unique identifier for the loading state
   * @param {boolean} isLoading - Loading state
   * @param {string} message - Optional loading message
   */
  const setLoading = useCallback((key, isLoading, message = '') => {
    setLoadingStates(prev => ({
      ...prev,
      [key]: {
        isLoading,
        message: message || prev[key]?.message || 'Loading...',
        timestamp: isLoading ? Date.now() : null
      }
    }));

    if (isLoading) {
      logger.info(`Loading started: ${key}`, 'LoadingState', { message });
    } else {
      logger.info(`Loading completed: ${key}`, 'LoadingState');
    }
  }, [logger]);

  /**
   * Set progress for a specific key
   * @param {string} key - Unique identifier for the progress
   * @param {number} value - Progress value (0-100)
   */
  const setProgressValue = useCallback((key, value) => {
    setProgress(prev => ({
      ...prev,
      [key]: Math.max(0, Math.min(100, value))
    }));
  }, []);

  /**
   * Check if any loading state is active
   * @returns {boolean}
   */
  const isAnyLoading = useCallback(() => {
    return Object.values(loadingStates).some(state => state.isLoading);
  }, [loadingStates]);

  /**
   * Check if a specific loading state is active
   * @param {string} key - Loading state key
   * @returns {boolean}
   */
  const isLoading = useCallback((key) => {
    return loadingStates[key]?.isLoading || false;
  }, [loadingStates]);

  /**
   * Get loading message for a specific key
   * @param {string} key - Loading state key
   * @returns {string}
   */
  const getLoadingMessage = useCallback((key) => {
    return loadingStates[key]?.message || 'Loading...';
  }, [loadingStates]);

  /**
   * Get progress value for a specific key
   * @param {string} key - Progress key
   * @returns {number}
   */
  const getProgress = useCallback((key) => {
    return progress[key] || 0;
  }, [progress]);

  /**
   * Clear all loading states
   */
  const clearAllLoading = useCallback(() => {
    setLoadingStates({});
    setProgress({});
    logger.info('All loading states cleared', 'LoadingState');
  }, [logger]);

  /**
   * Clear a specific loading state
   * @param {string} key - Loading state key
   */
  const clearLoading = useCallback((key) => {
    setLoadingStates(prev => {
      const newState = { ...prev };
      delete newState[key];
      return newState;
    });
    
    setProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[key];
      return newProgress;
    });
    
    logger.info(`Loading state cleared: ${key}`, 'LoadingState');
  }, [logger]);

  /**
   * Execute an async function with loading state
   * @param {string} key - Loading state key
   * @param {Function} asyncFn - Async function to execute
   * @param {string} message - Loading message
   * @returns {Promise} - Result of the async function
   */
  const withLoading = useCallback(async (key, asyncFn, message = '') => {
    try {
      setLoading(key, true, message);
      const result = await asyncFn();
      setLoading(key, false);
      return result;
    } catch (error) {
      setLoading(key, false);
      logger.error(`Error in loading operation ${key}: ${error?.toString?.() || String(error)}`, 'LoadingState');
      throw error;
    }
  }, [setLoading, logger]);

  /**
   * Execute an async function with progress tracking
   * @param {string} key - Loading state key
   * @param {Function} asyncFn - Async function that accepts a progress callback
   * @param {string} message - Loading message
   * @returns {Promise} - Result of the async function
   */
  const withProgress = useCallback(async (key, asyncFn, message = '') => {
    try {
      setLoading(key, true, message);
      setProgressValue(key, 0);
      
      const progressCallback = (value) => {
        setProgressValue(key, value);
      };
      
      const result = await asyncFn(progressCallback);
      setProgressValue(key, 100);
      setLoading(key, false);
      return result;
    } catch (error) {
      setLoading(key, false);
      setProgressValue(key, 0);
      logger.error(`Error in progress operation ${key}: ${error?.toString?.() || String(error)}`, 'LoadingState');
      throw error;
    }
  }, [setLoading, setProgressValue, logger]);

  /**
   * Get all active loading states
   * @returns {Object} - Object with active loading states
   */
  const getActiveLoadingStates = useCallback(() => {
    return Object.entries(loadingStates)
      .filter(([_, state]) => state.isLoading)
      .reduce((acc, [key, state]) => {
        acc[key] = state;
        return acc;
      }, {});
  }, [loadingStates]);

  /**
   * Get loading state summary
   * @returns {Object} - Summary of all loading states
   */
  const getLoadingSummary = useCallback(() => {
    const activeStates = getActiveLoadingStates();
    return {
      total: Object.keys(loadingStates).length,
      active: Object.keys(activeStates).length,
      activeStates,
      progress
    };
  }, [loadingStates, getActiveLoadingStates, progress]);

  return {
    // State
    loadingStates,
    progress,
    
    // Actions
    setLoading,
    setProgressValue,
    clearAllLoading,
    clearLoading,
    withLoading,
    withProgress,
    
    // Getters
    isAnyLoading,
    isLoading,
    getLoadingMessage,
    getProgress,
    getActiveLoadingStates,
    getLoadingSummary
  };
};

/**
 * Predefined loading state keys for common operations
 */
export const LOADING_KEYS = {
  // App initialization
  APP_INIT: 'app_init',
  SPLASH_SCREEN: 'splash_screen',
  
  // Location services
  LOCATION_PERMISSION: 'location_permission',
  LOCATION_FETCH: 'location_fetch',
  LOCATION_GEOCODE: 'location_geocode',
  
  // Notifications
  NOTIFICATION_PERMISSION: 'notification_permission',
  NOTIFICATION_SUBSCRIBE: 'notification_subscribe',
  NOTIFICATION_UNSUBSCRIBE: 'notification_unsubscribe',
  
  // Network operations
  API_CALL: 'api_call',
  WEATHER_FETCH: 'weather_fetch',
  DEVICE_REGISTRATION: 'device_registration',
  
  // Payment processing
  PAYMENT_INIT: 'payment_init',
  PAYMENT_PROCESS: 'payment_process',
  PAYMENT_CONFIRM: 'payment_confirm',
  
  // App updates
  UPDATE_CHECK: 'update_check',
  UPDATE_DOWNLOAD: 'update_download',
  UPDATE_APPLY: 'update_apply',
  
  // Navigation
  NAVIGATION: 'navigation',
  SCREEN_LOAD: 'screen_load',
  
  // Data operations
  DATA_LOAD: 'data_load',
  DATA_SAVE: 'data_save',
  DATA_SYNC: 'data_sync'
};

/**
 * Predefined loading messages for common operations
 */
export const LOADING_MESSAGES = {
  [LOADING_KEYS.APP_INIT]: 'Initializing app...',
  [LOADING_KEYS.SPLASH_SCREEN]: 'Loading...',
  [LOADING_KEYS.LOCATION_PERMISSION]: 'Requesting location permission...',
  [LOADING_KEYS.LOCATION_FETCH]: 'Getting your location...',
  [LOADING_KEYS.LOCATION_GEOCODE]: 'Finding your city...',
  [LOADING_KEYS.NOTIFICATION_PERMISSION]: 'Requesting notification permission...',
  [LOADING_KEYS.NOTIFICATION_SUBSCRIBE]: 'Subscribing to alerts...',
  [LOADING_KEYS.NOTIFICATION_UNSUBSCRIBE]: 'Unsubscribing from alerts...',
  [LOADING_KEYS.API_CALL]: 'Connecting to server...',
  [LOADING_KEYS.WEATHER_FETCH]: 'Fetching weather data...',
  [LOADING_KEYS.DEVICE_REGISTRATION]: 'Registering device...',
  [LOADING_KEYS.PAYMENT_INIT]: 'Initializing payment...',
  [LOADING_KEYS.PAYMENT_PROCESS]: 'Processing payment...',
  [LOADING_KEYS.PAYMENT_CONFIRM]: 'Confirming payment...',
  [LOADING_KEYS.UPDATE_CHECK]: 'Checking for updates...',
  [LOADING_KEYS.UPDATE_DOWNLOAD]: 'Downloading update...',
  [LOADING_KEYS.UPDATE_APPLY]: 'Applying update...',
  [LOADING_KEYS.NAVIGATION]: 'Loading...',
  [LOADING_KEYS.SCREEN_LOAD]: 'Loading screen...',
  [LOADING_KEYS.DATA_LOAD]: 'Loading data...',
  [LOADING_KEYS.DATA_SAVE]: 'Saving data...',
  [LOADING_KEYS.DATA_SYNC]: 'Syncing data...'
}; 