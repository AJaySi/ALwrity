/**
 * Shared toast notification utility
 * Provides a consistent way to show toast notifications across the app
 */

export type ToastType = 'error' | 'warning' | 'info' | 'success';

interface ToastOptions {
  /**
   * Duration in milliseconds before toast auto-dismisses
   * @default 5000 for info/warning, 7000 for error
   */
  duration?: number;
  
  /**
   * Position of the toast
   * @default 'top-right'
   */
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  
  /**
   * Maximum width of the toast
   * @default 400
   */
  maxWidth?: number;
}

/**
 * Show a toast notification using DOM-based approach
 * Works globally across the app, regardless of which component is mounted
 * 
 * @param message - The message to display
 * @param type - The type of toast (error, warning, info, success)
 * @param options - Optional configuration
 */
export function showToastNotification(
  message: string,
  type: ToastType = 'info',
  options: ToastOptions = {}
): void {
  const {
    duration,
    position = 'top-right',
    maxWidth = 400
  } = options;

  // Determine duration based on type if not specified
  const toastDuration = duration !== undefined
    ? duration
    : type === 'error' ? 7000 : 5000;

  // Determine background color based on type
  const bgColors: Record<ToastType, string> = {
    error: '#f44336',
    warning: '#ff9800',
    info: '#2196f3',
    success: '#4caf50'
  };

  // Determine position styles
  const positionStyles: Record<string, { top?: string; bottom?: string; left?: string; right?: string }> = {
    'top-left': { top: '20px', left: '20px' },
    'top-right': { top: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
    'bottom-right': { bottom: '20px', right: '20px' }
  };

  const pos = positionStyles[position] || positionStyles['top-right'];

  // Create toast element
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    ${pos.top ? `top: ${pos.top};` : ''}
    ${pos.bottom ? `bottom: ${pos.bottom};` : ''}
    ${pos.left ? `left: ${pos.left};` : ''}
    ${pos.right ? `right: ${pos.right};` : ''}
    padding: 16px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    font-size: 14px;
    z-index: 10000;
    max-width: ${maxWidth}px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateX(${position.includes('right') ? '100%' : position.includes('left') ? '-100%' : '0'});
    transition: transform 0.3s ease;
    background-color: ${bgColors[type] || bgColors.info};
    word-wrap: break-word;
    line-height: 1.5;
  `;

  toast.textContent = message;
  document.body.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.style.transform = 'translateX(0)';
  }, 100);

  // Remove after duration
  setTimeout(() => {
    const translateX = position.includes('right') ? '100%' : position.includes('left') ? '-100%' : '0';
    toast.style.transform = `translateX(${translateX})`;
    setTimeout(() => {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, 300);
  }, toastDuration);
}

/**
 * Show subscription-related toast notifications
 * Uses messages similar to SubscriptionExpiredModal
 */
export function showSubscriptionToast(
  message: string,
  type: 'error' | 'warning' = 'warning',
  options: ToastOptions = {}
): void {
  showToastNotification(message, type, {
    duration: type === 'error' ? 8000 : 6000, // Longer duration for subscription messages
    ...options
  });
}

/**
 * Show subscription expired toast
 */
export function showSubscriptionExpiredToast(): void {
  showSubscriptionToast(
    'Your subscription has expired. To continue using Alwrity and access all features, you need to renew your subscription.',
    'warning'
  );
}

/**
 * Show usage limit reached toast
 */
export function showUsageLimitToast(message?: string): void {
  showSubscriptionToast(
    message || 'You\'ve reached your monthly usage limit for this plan. Upgrade your plan to get higher limits.',
    'warning'
  );
}

