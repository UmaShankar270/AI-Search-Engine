import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-lg border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 text-brand-gray-700 dark:text-brand-gray-300 hover:bg-brand-gray-50 dark:hover:bg-brand-gray-800 transition-colors focus:outline-none cursor-pointer overflow-hidden"
      aria-label="Toggle theme"
      id="theme-toggle-btn"
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={theme}
          initial={{ y: -20, opacity: 0, rotate: -90 }}
          animate={{ y: 0, opacity: 1, rotate: 0 }}
          exit={{ y: 20, opacity: 0, rotate: 90 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="flex items-center justify-center w-5 h-5"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </motion.div>
      </AnimatePresence>
    </button>
  );
}
