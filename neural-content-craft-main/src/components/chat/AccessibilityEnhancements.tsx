import React, { useEffect, useState } from 'react';

// Keyboard Navigation Hook
export const useKeyboardNavigation = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip to main content
      if (e.key === 'Tab' && e.shiftKey && e.ctrlKey) {
        e.preventDefault();
        const mainContent = document.querySelector('[role="main"]') as HTMLElement;
        if (mainContent) {
          mainContent.focus();
          mainContent.scrollIntoView();
        }
      }
      
      // Skip to navigation
      if (e.key === 'Tab' && e.ctrlKey) {
        e.preventDefault();
        const navigation = document.querySelector('nav') as HTMLElement;
        if (navigation) {
          navigation.focus();
          navigation.scrollIntoView();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};

// Screen Reader Announcements Hook
export const useScreenReaderAnnouncements = () => {
  const [announcements, setAnnouncements] = useState<string[]>([]);

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncements(prev => [...prev, message]);
    
    // Remove announcement after 3 seconds
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(msg => msg !== message));
    }, 3000);
  };

  return { announcements, announce };
};

// Focus Management Hook
export const useFocusManagement = () => {
  const [focusHistory, setFocusHistory] = useState<HTMLElement[]>([]);

  const saveFocus = (element: HTMLElement) => {
    setFocusHistory(prev => [...prev.slice(-4), element]);
  };

  const restoreFocus = () => {
    const lastFocused = focusHistory[focusHistory.length - 1];
    if (lastFocused && document.contains(lastFocused)) {
      lastFocused.focus();
    }
  };

  const trapFocus = (container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  };

  return { saveFocus, restoreFocus, trapFocus };
};

// High Contrast Mode Detection
export const useHighContrastMode = () => {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    const checkHighContrast = () => {
      setIsHighContrast(window.matchMedia('(prefers-contrast: high)').matches);
    };

    checkHighContrast();
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    mediaQuery.addEventListener('change', checkHighContrast);

    return () => mediaQuery.removeEventListener('change', checkHighContrast);
  }, []);

  return isHighContrast;
};

// Reduced Motion Detection
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const checkReducedMotion = () => {
      setPrefersReducedMotion(window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    };

    checkReducedMotion();
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    mediaQuery.addEventListener('change', checkReducedMotion);

    return () => mediaQuery.removeEventListener('change', checkReducedMotion);
  }, []);

  return prefersReducedMotion;
};

// Color Scheme Detection
export const useColorScheme = () => {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark' | 'auto'>('auto');

  useEffect(() => {
    const checkColorScheme = () => {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setColorScheme('dark');
      } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
        setColorScheme('light');
      } else {
        setColorScheme('auto');
      }
    };

    checkColorScheme();
    const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const lightQuery = window.matchMedia('(prefers-color-scheme: light)');
    
    darkQuery.addEventListener('change', checkColorScheme);
    lightQuery.addEventListener('change', checkColorScheme);

    return () => {
      darkQuery.removeEventListener('change', checkColorScheme);
      lightQuery.removeEventListener('change', checkColorScheme);
    };
  }, []);

  return colorScheme;
};

// Accessibility Announcements Component
interface AccessibilityAnnouncementsProps {
  announcements: string[];
}

export const AccessibilityAnnouncements: React.FC<AccessibilityAnnouncementsProps> = ({ 
  announcements 
}) => {
  return (
    <div 
      aria-live="polite" 
      aria-atomic="true"
      className="sr-only"
    >
      {announcements.map((announcement, index) => (
        <div key={index}>{announcement}</div>
      ))}
    </div>
  );
};

// Skip Links Component
export const SkipLinks: React.FC = () => {
  return (
    <div className="sr-only focus-within:not-sr-only">
      <a 
        href="#main-content" 
        className="absolute top-4 left-4 z-50 bg-accent-primary text-background-primary px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2"
      >
        Skip to main content
      </a>
      <a 
        href="#navigation" 
        className="absolute top-4 left-32 z-50 bg-accent-primary text-background-primary px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2"
      >
        Skip to navigation
      </a>
      <a 
        href="#chat-input" 
        className="absolute top-4 left-64 z-50 bg-accent-primary text-background-primary px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2"
      >
        Skip to chat input
      </a>
    </div>
  );
};

// Focus Indicator Component
export const FocusIndicator: React.FC<{ 
  children: React.ReactNode; 
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <div className={`focus-within:ring-2 focus-within:ring-accent-primary focus-within:ring-offset-2 focus-within:ring-offset-background-primary ${className}`}>
      {children}
    </div>
  );
};

// ARIA Live Region for Dynamic Content
export const LiveRegion: React.FC<{
  message: string;
  priority?: 'polite' | 'assertive';
  className?: string;
}> = ({ message, priority = 'polite', className = '' }) => {
  return (
    <div 
      aria-live={priority}
      aria-atomic="true"
      className={`sr-only ${className}`}
    >
      {message}
    </div>
  );
};

// Keyboard Shortcuts Help Component
export const KeyboardShortcuts: React.FC = () => {
  const shortcuts = [
    { keys: 'Ctrl + K', description: 'Start new chat' },
    { keys: 'Ctrl + F', description: 'Toggle fullscreen' },
    { keys: 'Ctrl + /', description: 'Show help' },
    { keys: 'Tab', description: 'Navigate between elements' },
    { keys: 'Shift + Tab', description: 'Navigate backwards' },
    { keys: 'Enter', description: 'Send message' },
    { keys: 'Shift + Enter', description: 'New line in input' },
    { keys: 'Escape', description: 'Close dialogs' },
  ];

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-text-primary mb-4">Keyboard Shortcuts</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {shortcuts.map((shortcut, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
            <span className="text-text-secondary">{shortcut.description}</span>
            <kbd className="px-2 py-1 bg-background-primary border border-border-primary rounded text-xs font-mono text-text-primary">
              {shortcut.keys}
            </kbd>
          </div>
        ))}
      </div>
    </div>
  );
};

// Touch Gesture Support Hook
export const useTouchGestures = () => {
  const [gestures, setGestures] = useState({
    swipeLeft: false,
    swipeRight: false,
    swipeUp: false,
    swipeDown: false,
    pinch: false,
  });

  useEffect(() => {
    let startX = 0;
    let startY = 0;
    let startDistance = 0;

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      } else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        startDistance = Math.sqrt(dx * dx + dy * dy);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (e.changedTouches.length === 1) {
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        
        const minSwipeDistance = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          if (Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
              setGestures(prev => ({ ...prev, swipeRight: true }));
              setTimeout(() => setGestures(prev => ({ ...prev, swipeRight: false })), 100);
            } else {
              setGestures(prev => ({ ...prev, swipeLeft: true }));
              setTimeout(() => setGestures(prev => ({ ...prev, swipeLeft: false })), 100);
            }
          }
        } else {
          if (Math.abs(deltaY) > minSwipeDistance) {
            if (deltaY > 0) {
              setGestures(prev => ({ ...prev, swipeDown: true }));
              setTimeout(() => setGestures(prev => ({ ...prev, swipeDown: false })), 100);
            } else {
              setGestures(prev => ({ ...prev, swipeUp: true }));
              setTimeout(() => setGestures(prev => ({ ...prev, swipeUp: false })), 100);
            }
          }
        }
      }
    };

    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, []);

  return gestures;
};

export default {
  useKeyboardNavigation,
  useScreenReaderAnnouncements,
  useFocusManagement,
  useHighContrastMode,
  useReducedMotion,
  useColorScheme,
  useTouchGestures,
  AccessibilityAnnouncements,
  SkipLinks,
  FocusIndicator,
  LiveRegion,
  KeyboardShortcuts,
};
