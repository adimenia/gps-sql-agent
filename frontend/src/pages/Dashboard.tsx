import { useState, useEffect } from 'react'
import {
  Box,
  SimpleGrid,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Spinner,
} from '@chakra-ui/react'

interface DashboardStats {
  activities: number
  athletes: number
  events: number
  efforts: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Basic API call to get overview metrics
      const response = await fetch('/api/v1/dashboard/metrics/overview')
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard stats')
      }
      
      const data = await response.json()
      setStats(data.totals)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const cardBg = 'white'
  const borderColor = 'gray.200'

  if (loading) {
    return (
      <VStack gap={4} justify="center" align="center" minH="400px">
        <Spinner size="xl" color="brand.500" />
        <Text>Loading dashboard...</Text>
      </VStack>
    )
  }

  if (error) {
    return (
      <Box p={6} bg="red.50" border="1px" borderColor="red.200" borderRadius="md">
        <Text color="red.700" fontWeight="bold">Error loading dashboard!</Text>
        <Text color="red.600" mt={2}>{error}</Text>
        <Button mt={4} onClick={fetchDashboardStats} colorScheme="red" variant="outline">
          Retry
        </Button>
      </Box>
    )
  }

  return (
    <VStack gap={8} align="stretch">
      <Box>
        <Heading size="xl" mb={2} color="blue.600">
          Dashboard
        </Heading>
        <Text color="gray.600">
          Overview of your sports analytics data
        </Text>
      </Box>

      {stats && (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={6}>
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
            <Text fontSize="3xl" fontWeight="bold" color="blue.600">{stats.activities}</Text>
            <Text color="gray.600" fontSize="sm">Training Activities</Text>
            <Text color="gray.500" fontSize="xs">Total sessions recorded</Text>
          </Box>
          
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
            <Text fontSize="3xl" fontWeight="bold" color="blue.500">{stats.athletes}</Text>
            <Text color="gray.600" fontSize="sm">Athletes</Text>
            <Text color="gray.500" fontSize="xs">Active team members</Text>
          </Box>
          
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
            <Text fontSize="3xl" fontWeight="bold" color="orange.500">{stats.events}</Text>
            <Text color="gray.600" fontSize="sm">Performance Events</Text>
            <Text color="gray.500" fontSize="xs">Acceleration & movement data</Text>
          </Box>
          
          <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
            <Text fontSize="3xl" fontWeight="bold" color="green.500">{stats.efforts}</Text>
            <Text color="gray.600" fontSize="sm">Training Efforts</Text>
            <Text color="gray.500" fontSize="xs">Velocity & intensity metrics</Text>
          </Box>
        </SimpleGrid>
      )}

      <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
        <Heading size="md" mb={4}>
          Quick Actions
        </Heading>
        <HStack gap={4} wrap="wrap">
          <Button 
            onClick={() => window.location.href = '/chat'}
            colorScheme="blue"
            size="lg"
          >
            🤖 Ask the AI Agent
          </Button>
          <Button 
            onClick={fetchDashboardStats}
            colorScheme="green"
            variant="outline"
            size="lg"
          >
            🔄 Refresh Data
          </Button>
        </HStack>
      </Box>

      <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
        <Heading size="md" mb={4}>
          Getting Started
        </Heading>
        <VStack gap={4} align="stretch">
          <Box>
            <Heading size="sm" mb={2}>
              💬 Ask Questions
            </Heading>
            <Text color="gray.600" fontSize="sm">
              Go to the Chat Agent and ask questions like "Who are the fastest athletes?" or "Show me recent training data"
            </Text>
          </Box>
          <Box>
            <Heading size="sm" mb={2}>
              📊 View Analytics
            </Heading>
            <Text color="gray.600" fontSize="sm">
              The dashboard shows key metrics from your sports performance data
            </Text>
          </Box>
          <Box>
            <Heading size="sm" mb={2}>
              🔍 Explore Data
            </Heading>
            <Text color="gray.600" fontSize="sm">
              Use natural language to explore velocity, acceleration, distance, and training patterns
            </Text>
          </Box>
        </VStack>
      </Box>
    </VStack>
  )
}