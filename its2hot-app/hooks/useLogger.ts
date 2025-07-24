import { Platform } from 'react-native';
import * as Device from 'expo-device';

const BACKEND_URL = 'https://its2hot.org/api/log-debug';

async function sendLog(level: string, message: string, context?: string, extra?: any) {
  try {
    const payload = {
      level,
      message,
      context,
      extra,
      platform: Platform.OS,
      deviceName: Device.deviceName,
      deviceModel: Device.modelName,
      deviceId: Device.osBuildId,
      timestamp: new Date().toISOString(),
    };
    await fetch(BACKEND_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    // Fallback: log to console if network fails
    console.error('Failed to send log to backend:', err);
  }
}

export function useLogger() {
  return {
    log: (msg: string, ctx?: string, extra?: any) => sendLog('log', msg, ctx, extra),
    info: (msg: string, ctx?: string, extra?: any) => sendLog('info', msg, ctx, extra),
    warn: (msg: string, ctx?: string, extra?: any) => sendLog('warn', msg, ctx, extra),
    error: (msg: string, ctx?: string, extra?: any) => sendLog('error', msg, ctx, extra),
  };
}

export function logError(error: any, context?: string, extra?: any) {
  const msg = error?.toString?.() || String(error);
  sendLog('error', msg, context, extra);
} 