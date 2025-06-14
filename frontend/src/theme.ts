import { createSystem, defaultConfig } from '@chakra-ui/react'

const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        brand: {
          50: { value: '#e3f2fd' },
          100: { value: '#bbdefb' },
          200: { value: '#90caf9' },
          300: { value: '#64b5f6' },
          400: { value: '#42a5f5' },
          500: { value: '#2196f3' },
          600: { value: '#1e88e5' },
          700: { value: '#1976d2' },
          800: { value: '#1565c0' },
          900: { value: '#0d47a1' },
        },
        sports: {
          primary: { value: '#1976d2' },
          secondary: { value: '#42a5f5' },
          accent: { value: '#ff9800' },
          success: { value: '#4caf50' },
          warning: { value: '#ff9800' },
          error: { value: '#f44336' },
          background: { value: '#f5f5f5' },
          surface: { value: '#ffffff' },
        }
      },
      fonts: {
        heading: { value: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"` },
        body: { value: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"` },
      },
    },
    semanticTokens: {
      colors: {
        'sports.primary': { value: '{colors.sports.primary}' },
        'sports.secondary': { value: '{colors.sports.secondary}' },
        'sports.accent': { value: '{colors.sports.accent}' },
        'sports.success': { value: '{colors.sports.success}' },
        'sports.background': { value: '{colors.sports.background}' },
        'sports.surface': { value: '{colors.sports.surface}' },
      }
    },
  },
  globalCss: {
    body: {
      bg: 'sports.background',
      color: 'gray.800',
    },
  },
})

export default system