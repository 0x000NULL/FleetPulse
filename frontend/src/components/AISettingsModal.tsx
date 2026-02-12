import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, Key, Brain, ExternalLink, AlertCircle, CheckCircle, Loader, CreditCard, Zap, Bot } from 'lucide-react'

interface Props {
  isOpen: boolean
  onClose: () => void
  onConfigChange?: () => void
}

interface AIConfig {
  ai_enabled: boolean
  model?: string
  provider: 'anthropic' | 'openrouter' | 'demo'
  provider_name: string
}

type ProviderOption = 'anthropic' | 'openrouter' | 'demo'

export default function AISettingsModal({ isOpen, onClose, onConfigChange }: Props) {
  const [selectedProvider, setSelectedProvider] = useState<ProviderOption>('anthropic')
  const [apiKey, setApiKey] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [aiConfig, setAiConfig] = useState<AIConfig | null>(null)

  // Fetch current AI config when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchAIConfig()
    }
  }, [isOpen])

  const fetchAIConfig = async () => {
    try {
      const response = await fetch('/api/ai/config')
      if (response.ok) {
        const config = await response.json()
        setAiConfig(config)
      }
    } catch (error) {
      console.error('Failed to fetch AI config:', error)
    }
  }

  const handleSaveKey = async () => {
    // Demo mode doesn't require an API key
    if (selectedProvider === 'demo') {
      setIsLoading(true)
      setError('')
      setSuccess(false)

      try {
        const response = await fetch('/api/ai/config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ api_key: '', provider: 'demo' }),
        })

        if (response.ok) {
          setSuccess(true)
          await fetchAIConfig() // Refresh config
          onConfigChange?.()
          setTimeout(() => setSuccess(false), 3000)
        } else {
          const error = await response.json()
          setError(error.detail || 'Failed to set demo mode')
        }
      } catch (error) {
        setError('Network error. Please try again.')
      } finally {
        setIsLoading(false)
      }
      return
    }

    // For API providers, require a key
    if (!apiKey.trim()) {
      setError('Please enter an API key')
      return
    }

    setIsLoading(true)
    setError('')
    setSuccess(false)

    try {
      const response = await fetch('/api/ai/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          api_key: apiKey, 
          provider: selectedProvider 
        }),
      })

      if (response.ok) {
        const result = await response.json()
        setSuccess(true)
        setApiKey('') // Clear the input for security
        await fetchAIConfig() // Refresh config
        
        // Notify parent component
        onConfigChange?.()
        
        setTimeout(() => {
          setSuccess(false)
        }, 3000)
      } else {
        const error = await response.json()
        setError(error.detail || 'Failed to configure API key')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    setApiKey('')
    setError('')
    setSuccess(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="bg-gray-900 rounded-xl shadow-2xl border border-gray-800 w-full max-w-lg"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">AI Settings</h3>
              <p className="text-sm text-gray-400">Configure Claude AI for enhanced fleet intelligence</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Current Status */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Brain className="w-5 h-5 text-purple-400" />
              <span className="font-medium">AI Status</span>
            </div>
            
            {aiConfig ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  {aiConfig.ai_enabled ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                  )}
                  <span>
                    {aiConfig.ai_enabled 
                      ? `Active (${aiConfig.model})` 
                      : 'Demo Mode (Pattern Matching)'
                    }
                  </span>
                </div>
                <p className="text-gray-400">
                  Provider: {aiConfig.provider_name}
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Loader className="w-4 h-4 animate-spin" />
                Loading configuration...
              </div>
            )}
          </div>

          {/* Provider Options */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <label className="font-medium">Choose AI Provider</label>
            </div>
            
            {/* Anthropic API Key */}
            <div className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedProvider === 'anthropic' 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-gray-700 hover:border-gray-600'
            }`} onClick={() => setSelectedProvider('anthropic')}>
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={selectedProvider === 'anthropic'}
                  onChange={() => setSelectedProvider('anthropic')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-medium text-white">Anthropic API Key</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    Direct API access, pay per use. Get a key at console.anthropic.com
                  </p>
                </div>
              </div>
            </div>

            {/* OpenRouter */}
            <div className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedProvider === 'openrouter' 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-gray-700 hover:border-gray-600'
            }`} onClick={() => setSelectedProvider('openrouter')}>
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={selectedProvider === 'openrouter'}
                  onChange={() => setSelectedProvider('openrouter')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-medium text-white">OpenRouter</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    Use your Claude Max/Pro subscription. Free tier available. Get a key at openrouter.ai/keys
                  </p>
                </div>
              </div>
            </div>

            {/* Demo Mode */}
            <div className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedProvider === 'demo' 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-gray-700 hover:border-gray-600'
            }`} onClick={() => setSelectedProvider('demo')}>
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={selectedProvider === 'demo'}
                  onChange={() => setSelectedProvider('demo')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-medium text-white">Demo Mode</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    No key needed. Uses pattern matching for common fleet queries.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* API Key Input (only for providers that need keys) */}
          {selectedProvider !== 'demo' && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Key className="w-5 h-5 text-blue-400" />
                <label htmlFor="apiKey" className="font-medium">
                  {selectedProvider === 'anthropic' ? 'Anthropic API Key' : 'OpenRouter API Key'}
                </label>
              </div>
              
              <div className="space-y-2">
                <input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={
                    aiConfig?.ai_enabled && aiConfig.provider === selectedProvider
                      ? "API key is configured" 
                      : selectedProvider === 'anthropic' 
                        ? "sk-ant-..." 
                        : "sk-or-..."
                  }
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
                
                {error && (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </div>
                )}
                
                {success && (
                  <div className="flex items-center gap-2 text-green-400 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    Configuration saved successfully!
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Save Button */}
          <div>
            <button
              onClick={handleSaveKey}
              disabled={isLoading || (selectedProvider !== 'demo' && !apiKey.trim())}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  {selectedProvider === 'demo' ? 'Setting up...' : 'Validating...'}
                </>
              ) : selectedProvider === 'demo' ? (
                'Use Demo Mode'
              ) : (
                `Configure ${selectedProvider === 'anthropic' ? 'Anthropic' : 'OpenRouter'} API Key`
              )}
            </button>
          </div>

          {/* Information based on selected provider */}
          {selectedProvider === 'anthropic' && (
            <div className="bg-blue-900/20 border border-blue-800/30 rounded-lg p-4">
              <h4 className="font-medium text-blue-300 mb-2">How to get an Anthropic API key:</h4>
              <div className="space-y-2 text-sm text-blue-200">
                <p>1. Visit <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="underline inline-flex items-center gap-1">
                  console.anthropic.com <ExternalLink className="w-3 h-3" />
                </a></p>
                <p>2. Sign up or log in to your account</p>
                <p>3. Navigate to API Keys and create a new key</p>
                <p>4. Copy and paste it here</p>
              </div>
            </div>
          )}

          {selectedProvider === 'openrouter' && (
            <div className="bg-purple-900/20 border border-purple-800/30 rounded-lg p-4">
              <h4 className="font-medium text-purple-300 mb-2">How to get an OpenRouter API key:</h4>
              <div className="space-y-2 text-sm text-purple-200">
                <p>1. Visit <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="underline inline-flex items-center gap-1">
                  openrouter.ai/keys <ExternalLink className="w-3 h-3" />
                </a></p>
                <p>2. Sign up or log in to your account</p>
                <p>3. Create a new API key</p>
                <p>4. Copy and paste it here</p>
              </div>
              <div className="mt-3 pt-3 border-t border-purple-800/30">
                <p className="text-xs text-purple-300">
                  <strong>Tip:</strong> If you have Claude Max ($100/mo) or Pro ($20/mo), you can use your subscription credits instead of paying per API call.
                </p>
              </div>
            </div>
          )}

          {selectedProvider === 'demo' && (
            <div className="bg-yellow-900/20 border border-yellow-800/30 rounded-lg p-4">
              <h4 className="font-medium text-yellow-300 mb-2">Demo Mode</h4>
              <p className="text-sm text-yellow-200">
                Demo mode uses intelligent pattern-matching for common fleet queries. 
                It works without any API keys but provides less sophisticated responses than full AI.
              </p>
              <div className="mt-3 pt-3 border-t border-yellow-800/30">
                <p className="text-xs text-yellow-300">
                  Good for: Basic fleet queries, safety scores, idle analysis, maintenance alerts.
                </p>
              </div>
            </div>
          )}

          {/* Privacy notice for all modes */}
          <div className="bg-gray-800/30 border border-gray-700/30 rounded-lg p-4">
            <p className="text-xs text-gray-400">
              <strong>Privacy:</strong> API keys are stored in memory only and never saved to disk.
              You'll need to re-enter keys after server restarts.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}