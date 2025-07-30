import { Platform } from 'react-native';

// Accessibility constants for consistent usage across the app
export const ACCESSIBILITY = {
  // Screen reader labels
  LABELS: {
    // Home Screen
    SUBSCRIBE_BUTTON: 'Subscribe to temperature alerts',
    UNSUBSCRIBE_BUTTON: 'Unsubscribe from temperature alerts',
    SHOP_BUTTON: 'Go to shop to buy t-shirts',
    LOCATION_BUTTON: 'Set your location for accurate alerts',
    MANUAL_LOCATION_INPUT: 'Enter your city or location',
    MANUAL_LOCATION_SUBMIT: 'Submit location',
    
    // Shop Screen
    DESIGN_SELECTION: 'Select t-shirt design',
    COLOR_SELECTION: 'Select t-shirt color',
    SIZE_SELECTION: 'Select t-shirt size',
    QUANTITY_INCREASE: 'Increase quantity',
    QUANTITY_DECREASE: 'Decrease quantity',
    QUANTITY_DISPLAY: 'Quantity selected',
    BUY_BUTTON: 'Buy t-shirt',
    VIEW_FRONT: 'View front of t-shirt',
    VIEW_BACK: 'View back of t-shirt',
    
    // Navigation
    BACK_BUTTON: 'Go back',
    HOME_TAB: 'Home screen',
    SHOP_TAB: 'Shop screen',
    EXPLORE_TAB: 'Explore screen',
    
    // General
    LOADING: 'Loading',
    ERROR: 'Error occurred',
    SUCCESS: 'Success',
    CLOSE: 'Close',
    CANCEL: 'Cancel',
    CONFIRM: 'Confirm',
    OK: 'OK',
  },
  
  // Hints for screen readers
  HINTS: {
    SUBSCRIBE_BUTTON: 'Double tap to subscribe to temperature alerts',
    UNSUBSCRIBE_BUTTON: 'Double tap to unsubscribe from temperature alerts',
    SHOP_BUTTON: 'Double tap to go to the shop',
    LOCATION_BUTTON: 'Double tap to set your location',
    MANUAL_LOCATION_INPUT: 'Type your city or location name',
    MANUAL_LOCATION_SUBMIT: 'Double tap to submit your location',
    
    DESIGN_SELECTION: 'Double tap to select this design',
    COLOR_SELECTION: 'Double tap to select this color',
    SIZE_SELECTION: 'Double tap to select this size',
    QUANTITY_INCREASE: 'Double tap to increase quantity',
    QUANTITY_DECREASE: 'Double tap to decrease quantity',
    BUY_BUTTON: 'Double tap to purchase this t-shirt',
    VIEW_FRONT: 'Double tap to view front of t-shirt',
    VIEW_BACK: 'Double tap to view back of t-shirt',
  },
  
  // Roles for screen readers
  ROLES: {
    BUTTON: 'button',
    LINK: 'link',
    HEADER: 'header',
    IMAGE: 'image',
    TEXT: 'text',
    ADJUSTABLE: 'adjustable',
    TAB: 'tab',
    TABLIST: 'tablist',
    LIST: 'list',
    LISTITEM: 'listitem',
    SEARCH: 'search',
    SPINBUTTON: 'spinbutton',
    SWITCH: 'switch',
    CHECKBOX: 'checkbox',
    RADIO: 'radio',
    COMBOBOX: 'combobox',
    MENU: 'menu',
    MENUITEM: 'menuitem',
    PROGRESSBAR: 'progressbar',
    SLIDER: 'slider',
    TABPANEL: 'tabpanel',
    TOOLBAR: 'toolbar',
    TOOLTIP: 'tooltip',
    GRID: 'grid',
    GRIDCELL: 'gridcell',
    COLUMNHEADER: 'columnheader',
    ROWHEADER: 'rowheader',
    ROW: 'row',
    ROWGROUP: 'rowgroup',
    COLUMN: 'column',
    COLUMNGROUP: 'columngroup',
    TREE: 'tree',
    TREEITEM: 'treeitem',
    TREEITEMSELECTED: 'treeitemselected',
    TREEITEMEXPANDED: 'treeitemexpanded',
    TREEITEMCOLLAPSED: 'treeitemcollapsed',
  },
  
  // States for screen readers
  STATES: {
    SELECTED: 'selected',
    CHECKED: 'checked',
    UNCHECKED: 'unchecked',
    DISABLED: 'disabled',
    EXPANDED: 'expanded',
    COLLAPSED: 'collapsed',
    BUSY: 'busy',
    REQUIRED: 'required',
    INVALID: 'invalid',
    VALID: 'valid',
  },
};

// Helper function to create accessibility props
export const createAccessibilityProps = (label, hint = null, role = null, state = null) => {
  const props = {
    accessible: true,
    accessibilityLabel: label,
  };
  
  if (hint) {
    props.accessibilityHint = hint;
  }
  
  if (role) {
    props.accessibilityRole = role;
  }
  
  if (state) {
    props.accessibilityState = state;
  }
  
  return props;
};

// Helper function for button accessibility
export const createButtonAccessibility = (label, hint = null, disabled = false) => {
  return createAccessibilityProps(
    label,
    hint || `Double tap to ${label.toLowerCase()}`,
    ACCESSIBILITY.ROLES.BUTTON,
    disabled ? { disabled: true } : null
  );
};

// Helper function for image accessibility
export const createImageAccessibility = (description, decorative = false) => {
  return {
    accessible: true,
    accessibilityLabel: description,
    accessibilityRole: ACCESSIBILITY.ROLES.IMAGE,
    accessibilityElementsHidden: decorative,
    importantForAccessibility: decorative ? 'no' : 'yes',
  };
};

// Helper function for text accessibility
export const createTextAccessibility = (text, role = ACCESSIBILITY.ROLES.TEXT) => {
  return {
    accessible: true,
    accessibilityLabel: text,
    accessibilityRole: role,
  };
};

// Helper function for input accessibility
export const createInputAccessibility = (label, hint = null, required = false) => {
  return createAccessibilityProps(
    label,
    hint,
    ACCESSIBILITY.ROLES.TEXT,
    required ? { required: true } : null
  );
};

// Helper function for list accessibility
export const createListAccessibility = (items, itemLabels) => {
  return {
    accessible: true,
    accessibilityRole: ACCESSIBILITY.ROLES.LIST,
    accessibilityLabel: `${items.length} items`,
    accessibilityHint: `List with ${items.length} items`,
  };
};

// Helper function for tab accessibility
export const createTabAccessibility = (label, selected = false) => {
  return createAccessibilityProps(
    label,
    `Double tap to select ${label}`,
    ACCESSIBILITY.ROLES.TAB,
    { selected }
  );
};

// Helper function for slider accessibility
export const createSliderAccessibility = (label, value, min, max) => {
  return {
    accessible: true,
    accessibilityLabel: label,
    accessibilityRole: ACCESSIBILITY.ROLES.SLIDER,
    accessibilityValue: {
      min,
      max,
      now: value,
    },
    accessibilityHint: `Adjust ${label} by swiping up or down`,
  };
};

// Helper function for switch accessibility
export const createSwitchAccessibility = (label, value) => {
  return {
    accessible: true,
    accessibilityLabel: label,
    accessibilityRole: ACCESSIBILITY.ROLES.SWITCH,
    accessibilityState: { checked: value },
    accessibilityHint: `Double tap to ${value ? 'disable' : 'enable'} ${label}`,
  };
};

// Helper function for modal accessibility
export const createModalAccessibility = (title, description) => {
  return {
    accessible: true,
    accessibilityLabel: title,
    accessibilityHint: description,
    accessibilityRole: ACCESSIBILITY.ROLES.ADJUSTABLE,
  };
};

// Platform-specific accessibility helpers
export const getPlatformAccessibility = () => {
  if (Platform.OS === 'ios') {
    return {
      // iOS-specific accessibility features
      supportsVoiceOver: true,
      supportsSwitchControl: true,
      supportsReduceMotion: true,
      supportsReduceTransparency: true,
      supportsIncreaseContrast: true,
      supportsBoldText: true,
      supportsLargerText: true,
    };
  } else if (Platform.OS === 'android') {
    return {
      // Android-specific accessibility features
      supportsTalkBack: true,
      supportsSwitchAccess: true,
      supportsHighContrast: true,
      supportsLargeText: true,
    };
  }
  return {};
};

// Helper function to check if accessibility is enabled
export const isAccessibilityEnabled = () => {
  // This would typically check the device's accessibility settings
  // For now, we'll assume it's enabled and let the OS handle it
  return true;
};

// Helper function for dynamic text sizing
export const getAccessibleFontSize = (baseSize) => {
  // This would typically check the device's text size settings
  // For now, we'll return the base size
  return baseSize;
};

// Helper function for color contrast
export const getAccessibleColors = (baseColors) => {
  // This would typically check the device's contrast settings
  // For now, we'll return the base colors
  return baseColors;
};

// Helper function for motion reduction
export const shouldReduceMotion = () => {
  // This would typically check the device's motion settings
  // For now, we'll return false
  return false;
};

export default ACCESSIBILITY; 