import { motion } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 dark:bg-gray-800/50 dark:hover:bg-gray-700/50 
                 light:bg-gray-200/50 light:hover:bg-gray-300/50 backdrop-blur-sm border border-gray-700/50 
                 dark:border-gray-700/50 light:border-gray-300/50 transition-all duration-200"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{ 
          rotate: theme === 'dark' ? 0 : 180,
          scale: theme === 'dark' ? 1 : 0.8
        }}
        transition={{ type: "spring", stiffness: 200, damping: 20 }}
        className="w-5 h-5 text-gray-300 dark:text-gray-300 light:text-gray-700"
      >
        {theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
      </motion.div>
    </motion.button>
  )
}