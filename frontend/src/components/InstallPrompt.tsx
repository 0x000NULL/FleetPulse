import React, { useState, useEffect } from 'react'
import { X, Download, Smartphone, Monitor } from 'lucide-react'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const InstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)
  const [isInstalled, setIsInstalled] = useState(false)

  useEffect(() => {
    // Check if already installed
    const checkIfInstalled = () => {
      // Check if running in standalone mode (installed)
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                          (window.navigator as any).standalone === true
      
      setIsInstalled(isStandalone)
    }

    // Check installation status on load
    checkIfInstalled()

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      const promptEvent = e as BeforeInstallPromptEvent
      setDeferredPrompt(promptEvent)
      
      // Check if user has previously dismissed the install prompt
      const dismissed = localStorage.getItem('installPromptDismissed')
      const dismissedTime = dismissed ? parseInt(dismissed) : 0
      const weekInMs = 7 * 24 * 60 * 60 * 1000
      
      // Show prompt if not dismissed or dismissed more than a week ago
      if (!dismissed || Date.now() - dismissedTime > weekInMs) {
        setShowPrompt(true)
      }
    }

    // Listen for app installation
    const handleAppInstalled = () => {
      console.log('FleetPulse: App was installed')
      setIsInstalled(true)
      setShowPrompt(false)
      setDeferredPrompt(null)
      localStorage.removeItem('installPromptDismissed')
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleAppInstalled)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('appinstalled', handleAppInstalled)
    }
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) return

    try {
      await deferredPrompt.prompt()
      const choiceResult = await deferredPrompt.userChoice
      
      if (choiceResult.outcome === 'accepted') {
        console.log('FleetPulse: User accepted the install prompt')
      } else {
        console.log('FleetPulse: User dismissed the install prompt')
      }
      
      setDeferredPrompt(null)
      setShowPrompt(false)
    } catch (error) {
      console.error('FleetPulse: Install prompt failed:', error)
    }
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    // Remember dismissal for a week
    localStorage.setItem('installPromptDismissed', Date.now().toString())
  }

  // Don't show if already installed or prompt not available
  if (isInstalled || !showPrompt || !deferredPrompt) {
    return null
  }

  const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

  return (
    <div className="fixed top-4 left-4 right-4 z-50 mx-auto max-w-sm">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg backdrop-blur-sm bg-opacity-95">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 p-2 bg-blue-500/20 rounded-lg">
            {isMobile ? (
              <Smartphone className="w-5 h-5 text-blue-400" />
            ) : (
              <Monitor className="w-5 h-5 text-blue-400" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-white mb-1">
              Install FleetPulse
            </h3>
            <p className="text-sm text-gray-300 mb-3">
              {isMobile 
                ? "Add FleetPulse to your home screen for quick access to your fleet dashboard"
                : "Install FleetPulse as an app for faster access and offline capabilities"
              }
            </p>
            
            <div className="flex gap-2">
              <button
                onClick={handleInstall}
                className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
              >
                <Download className="w-4 h-4" />
                Install
              </button>
              
              <button
                onClick={handleDismiss}
                className="px-3 py-2 text-gray-300 hover:text-white text-sm font-medium transition-colors"
              >
                Not now
              </button>
            </div>
          </div>
          
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default InstallPrompt