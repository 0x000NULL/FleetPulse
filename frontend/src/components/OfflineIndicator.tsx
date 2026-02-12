import React, { useState, useEffect } from 'react'
import { WifiOff, X } from 'lucide-react'

const OfflineIndicator: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [showIndicator, setShowIndicator] = useState(!navigator.onLine)
  const [wasOffline, setWasOffline] = useState(false)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      
      // If user was offline, show a brief "back online" message
      if (wasOffline) {
        setShowIndicator(true)
        setTimeout(() => {
          setShowIndicator(false)
          setWasOffline(false)
        }, 3000) // Hide after 3 seconds
      } else {
        setShowIndicator(false)
      }
    }

    const handleOffline = () => {
      setIsOnline(false)
      setShowIndicator(true)
      setWasOffline(true)
    }

    // Add event listeners
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [wasOffline])

  const handleDismiss = () => {
    setShowIndicator(false)
  }

  if (!showIndicator) {
    return null
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-sm">
      <div className={`rounded-lg p-3 shadow-lg backdrop-blur-sm ${
        isOnline 
          ? 'bg-green-600/90 border border-green-500/50' 
          : 'bg-orange-600/90 border border-orange-500/50'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`flex-shrink-0 p-1.5 rounded-lg ${
            isOnline ? 'bg-green-500/30' : 'bg-orange-500/30'
          }`}>
            {isOnline ? (
              <div className="w-4 h-4 bg-green-400 rounded-full animate-pulse" />
            ) : (
              <WifiOff className="w-4 h-4 text-orange-200" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white">
              {isOnline ? 'Back Online!' : 'You\'re Offline'}
            </p>
            <p className="text-xs text-white/80">
              {isOnline 
                ? 'FleetPulse is syncing the latest data'
                : 'Showing cached data — some features may be limited'
              }
            </p>
          </div>
          
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 text-white/60 hover:text-white transition-colors"
            aria-label="Dismiss notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default OfflineIndicator