import React from 'react';

// CSS-based animated background component
const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background-primary via-background-secondary to-background-primary" />
      
      {/* Animated particles */}
      <div className="absolute inset-0">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-accent-primary/30 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 2}s`,
            }}
          />
        ))}
      </div>
      
      {/* Floating circles */}
      <div className="absolute inset-0">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-accent-primary/20"
            style={{
              width: `${20 + Math.random() * 40}px`,
              height: `${20 + Math.random() * 40}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float ${6 + Math.random() * 4}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>
      
      {/* Neural network pattern */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="neural-grid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="10" cy="10" r="1" fill="#00D9FF" opacity="0.3" />
              <line x1="10" y1="10" x2="30" y2="10" stroke="#8B5CF6" strokeWidth="0.5" opacity="0.2" />
              <line x1="10" y1="10" x2="10" y2="30" stroke="#8B5CF6" strokeWidth="0.5" opacity="0.2" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#neural-grid)" />
        </svg>
      </div>
      
      {/* Glowing orbs */}
      <div className="absolute inset-0">
        <div
          className="absolute w-32 h-32 bg-accent-primary/10 rounded-full blur-xl animate-pulse"
          style={{
            left: '20%',
            top: '30%',
            animationDuration: '4s',
          }}
        />
        <div
          className="absolute w-24 h-24 bg-accent-secondary/10 rounded-full blur-xl animate-pulse"
          style={{
            right: '25%',
            bottom: '20%',
            animationDuration: '5s',
            animationDelay: '1s',
          }}
        />
        <div
          className="absolute w-20 h-20 bg-accent-tertiary/10 rounded-full blur-xl animate-pulse"
          style={{
            left: '60%',
            top: '60%',
            animationDuration: '6s',
            animationDelay: '2s',
          }}
        />
      </div>
    </div>
  );
};

const ThreeBackground = AnimatedBackground;

export default ThreeBackground;