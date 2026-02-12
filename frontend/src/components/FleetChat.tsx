import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'
import { Send, Bot, User, TrendingUp, AlertTriangle, Map, Clock } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  data?: any
  chart?: 'bar' | 'line' | 'pie'
}

interface Props {
  isOpen: boolean
  onClose: () => void
}

const responses = {
  safetyScores: {
    pattern: /(safety|scores?|safest|dangerous|accident|incident)/i,
    response: "Based on current safety analytics, here are the safety scores by location:",
    data: [
      { location: 'Downtown', score: 94, color: '#10b981' },
      { location: 'Fremont', score: 93, color: '#10b981' },
      { location: 'McCarran', score: 92, color: '#10b981' },
      { location: 'Henderson', score: 91, color: '#10b981' },
      { location: 'Summerlin', score: 89, color: '#f59e0b' },
      { location: 'The Strip', score: 88, color: '#f59e0b' },
      { location: 'W Sahara', score: 87, color: '#f59e0b' },
      { location: 'N Las Vegas', score: 85, color: '#ef4444' }
    ],
    chart: 'bar' as const,
    insight: "Downtown and Fremont lead with 94% and 93% safety scores. N Las Vegas needs attention with 85% - recommend driver coaching program."
  },
  
  idleTime: {
    pattern: /(idle|idling|waste|wasted|stationary|parked)/i,
    response: "Here's the idle time analysis across locations:",
    data: [
      { location: 'W Sahara', minutes: 180, color: '#ef4444' },
      { location: 'N Las Vegas', minutes: 165, color: '#ef4444' },
      { location: 'The Strip', minutes: 120, color: '#f59e0b' },
      { location: 'Summerlin', minutes: 95, color: '#f59e0b' },
      { location: 'McCarran', minutes: 75, color: '#10b981' },
      { location: 'Henderson', minutes: 65, color: '#10b981' },
      { location: 'Downtown', minutes: 45, color: '#10b981' },
      { location: 'Fremont', minutes: 35, color: '#10b981' }
    ],
    chart: 'bar' as const,
    insight: "W Sahara has 3x more idle time than fleet average (60min). Vehicle #42 has been stationary for 6 hours outside its zone - dispatching maintenance check."
  },

  fuelEfficiency: {
    pattern: /(fuel|gas|efficiency|consumption|cost|mpg)/i,
    response: "Fuel efficiency trends over the last 7 days:",
    data: [
      { day: 'Mon', efficiency: 8.2 },
      { day: 'Tue', efficiency: 7.8 },
      { day: 'Wed', efficiency: 8.5 },
      { day: 'Thu', efficiency: 8.1 },
      { day: 'Fri', efficiency: 7.9 },
      { day: 'Sat', efficiency: 8.3 },
      { day: 'Sun', efficiency: 8.6 }
    ],
    chart: 'line' as const,
    insight: "Current average: 8.2 L/100km. Tuesday showed 7.8 L/100km - likely due to highway routes. Weekend efficiency improves due to local trips."
  },

  recommendations: {
    pattern: /(recommend|suggest|improve|optimize|save|cost)/i,
    response: "AI-generated cost optimization recommendations:",
    data: [
      { category: 'Route Optimization', savings: 2400, color: '#10b981' },
      { category: 'Idle Reduction', savings: 1800, color: '#3b82f6' },
      { category: 'Maintenance Scheduling', savings: 1200, color: '#8b5cf6' },
      { category: 'Driver Training', savings: 900, color: '#f59e0b' }
    ],
    chart: 'pie' as const,
    insight: "Potential monthly savings: $6,300. Top recommendation: Implement AI route optimization for 15% fuel savings. Start with W Sahara location."
  },

  utilization: {
    pattern: /(utilization|busy|active|usage|demand|peak)/i,
    response: "Fleet utilization patterns throughout the day:",
    data: [
      { hour: '6AM', rate: 24 },
      { hour: '8AM', rate: 56 },
      { hour: '10AM', rate: 70 },
      { hour: '12PM', rate: 84 },
      { hour: '2PM', rate: 76 },
      { hour: '4PM', rate: 90 },
      { hour: '6PM', rate: 64 },
      { hour: '8PM', rate: 36 },
      { hour: '10PM', rate: 16 }
    ],
    chart: 'line' as const,
    insight: "Peak utilization at 4PM (90%). Low utilization 6-10AM suggests opportunity for maintenance windows. Consider surge pricing during peak hours."
  },

  maintenance: {
    pattern: /(maintenance|repair|service|check|due)/i,
    response: "Predictive maintenance insights:",
    data: [
      { priority: 'Critical', count: 3, color: '#ef4444' },
      { priority: 'High', count: 7, color: '#f59e0b' },
      { priority: 'Medium', count: 12, color: '#3b82f6' },
      { priority: 'Low', count: 28, color: '#10b981' }
    ],
    chart: 'pie' as const,
    insight: "3 vehicles need immediate attention. Vehicle #23 shows unusual brake wear patterns. Vehicle #45 due for oil change in 2 days. Schedule during 6-8AM low utilization window."
  }
}

const quickQueries = [
  { text: "Which location has the best safety scores?", icon: "🛡️" },
  { text: "Show me vehicles that idled more than 30 min today", icon: "⏱️" },
  { text: "What are the cost-saving recommendations?", icon: "💰" },
  { text: "How is our fuel efficiency trending?", icon: "⛽" },
  { text: "When is peak fleet utilization?", icon: "📈" },
  { text: "Any maintenance predictions?", icon: "🔧" }
]

export default function FleetChat({ isOpen, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your fleet intelligence assistant. Ask me anything about vehicle performance, safety scores, cost optimization, or maintenance predictions. I can provide real-time insights and data visualizations.",
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const generateResponse = async (userMessage: string): Promise<{ content: string; data?: any; chart?: string; insights?: string[] }> => {
    try {
      // Call the backend AI API
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI response')
      }

      const data = await response.json()
      
      return {
        content: data.response,
        data: data.data,
        chart: data.chart_type,
        insights: data.insights
      }
    } catch (error) {
      console.error('AI API Error:', error)
      
      // Fallback to pattern matching
      const message = userMessage.toLowerCase()
      
      for (const [key, responseData] of Object.entries(responses)) {
        if (responseData.pattern.test(message)) {
          return {
            content: responseData.response,
            data: responseData.data,
            chart: responseData.chart,
            insights: [responseData.insight]
          }
        }
      }

      // Default responses for other patterns
      if (message.includes('hello') || message.includes('hi')) {
        return { content: "Hello! I'm here to help you analyze your fleet data. What would you like to know?" }
      }
      
      if (message.includes('help')) {
        return { content: "I can help you with:\n• Safety scores and incident analysis\n• Idle time and fuel efficiency\n• Cost optimization recommendations\n• Fleet utilization patterns\n• Predictive maintenance insights\n\nJust ask me a question in natural language!" }
      }

      return { 
        content: "I understand you're asking about fleet operations. Let me analyze that... Based on current data patterns, I'd recommend checking the analytics dashboard for detailed metrics. You can also try asking about specific topics like safety scores, fuel efficiency, or maintenance predictions." 
      }
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    const messageText = inputValue
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Get AI response
      const response = await generateResponse(messageText)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.content,
        timestamp: new Date(),
        data: response.data,
        chart: response.chart as any
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Add insights as follow-up messages if available
      if (response.insights && response.insights.length > 0) {
        setTimeout(() => {
          const insightMessages = response.insights!.map((insight, index) => ({
            id: (Date.now() + 2 + index).toString(),
            type: 'assistant' as const,
            content: `💡 **AI Insight:** ${insight}`,
            timestamp: new Date()
          }))
          
          setMessages(prev => [...prev, ...insightMessages])
          setIsTyping(false)
        }, 1000)
      } else {
        setIsTyping(false)
      }
    } catch (error) {
      console.error('Error getting AI response:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "I'm experiencing some technical difficulties. Please try again or ask about specific topics like safety scores, fuel efficiency, or maintenance predictions.",
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
      setIsTyping(false)
    }
  }

  const handleQuickQuery = (query: string) => {
    setInputValue(query)
  }

  const renderChart = (message: Message) => {
    if (!message.data || !message.chart) return null

    const chartProps = {
      width: "100%",
      height: 200,
      data: message.data
    }

    switch (message.chart) {
      case 'bar':
        return (
          <ResponsiveContainer {...chartProps}>
            <BarChart data={message.data}>
              <XAxis dataKey="location" stroke="#9ca3af" fontSize={12} angle={-45} textAnchor="end" height={60} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Bar dataKey="score" radius={[4, 4, 0, 0]} fill="#3b82f6" />
              <Bar dataKey="minutes" radius={[4, 4, 0, 0]} fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        )
      
      case 'line':
        return (
          <ResponsiveContainer {...chartProps}>
            <LineChart data={message.data}>
              <XAxis dataKey="day" stroke="#9ca3af" fontSize={12} />
              <XAxis dataKey="hour" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Line type="monotone" dataKey="efficiency" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} />
              <Line type="monotone" dataKey="rate" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        )
      
      case 'pie':
        return (
          <ResponsiveContainer {...chartProps}>
            <PieChart>
              <Pie
                data={message.data}
                cx="50%"
                cy="50%"
                outerRadius={80}
                innerRadius={30}
                paddingAngle={2}
                dataKey="savings"
                nameKey="category"
              >
                {message.data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Pie
                data={message.data}
                cx="50%"
                cy="50%"
                outerRadius={80}
                innerRadius={30}
                paddingAngle={2}
                dataKey="count"
                nameKey="priority"
              >
                {message.data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
            </PieChart>
          </ResponsiveContainer>
        )
      
      default:
        return null
    }
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="bg-gray-900 rounded-xl shadow-2xl border border-gray-800 w-full max-w-2xl h-[600px] flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold">Fleet Intelligence Assistant</h3>
              <p className="text-xs text-gray-400">Powered by AI • Real-time Analytics</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-blue-600' 
                    : 'bg-gradient-to-r from-purple-500 to-pink-600'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                  <div className={`inline-block p-3 rounded-xl max-w-[80%] ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100'
                  }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    {message.data && message.chart && (
                      <div className="mt-3 p-2 bg-gray-700/50 rounded-lg">
                        {renderChart(message)}
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800 rounded-xl p-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Query Buttons */}
        <div className="p-4 border-t border-gray-800">
          <p className="text-xs text-gray-400 mb-3">Quick queries:</p>
          <div className="grid grid-cols-2 gap-2 mb-4">
            {quickQueries.slice(0, 4).map((query, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuery(query.text)}
                className="text-xs p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-colors flex items-center gap-2"
              >
                <span>{query.icon}</span>
                <span className="truncate">{query.text}</span>
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about fleet performance, safety, costs..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isTyping}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}