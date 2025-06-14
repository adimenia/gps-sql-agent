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
import SimpleLineChart from '../components/charts/SimpleLineChart'

interface DashboardStats {
  activities: number
  athletes: number
  events: number
  efforts: number
}

interface ChartData {
  x: string
  velocity: number
  acceleration: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [chartLoading, setChartLoading] = useState(false)
  const [days, setDays] = useState(14)

  useEffect(() => {
    fetchDashboardStats()
    fetchChartData()
  }, [])

  useEffect(() => {
    fetchChartData()
  }, [days])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Basic API call to get overview metrics
      const response = await fetch('http://localhost:8001/api/v1/dashboard/metrics/overview')
      
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

  const fetchChartData = async () => {
    try {
      setChartLoading(true)
      
      const response = await fetch(`http://localhost:8001/api/v1/dashboard/charts/performance-trends?days=${days}&group_by=day`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch chart data')
      }
      
      const data = await response.json()
      
      // Transform the data for our chart
      const transformedData: ChartData[] = data.chart_data.map((item: any) => ({
        x: item.date,
        velocity: item.avg_velocity,
        acceleration: item.avg_acceleration
      }))
      
      setChartData(transformedData)
    } catch (err) {
      console.error('Error fetching chart data:', err)
      // Don't set error state for chart, just log it
    } finally {
      setChartLoading(false)
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

      {/* Performance Trends Chart */}
      <Box p={6} bg={cardBg} borderRadius="lg" shadow="md" border="1px" borderColor={borderColor}>
        <VStack gap={4} align="stretch">
          <HStack justify="space-between" align="center" wrap="wrap" gap={4}>
            <Box>
              <Heading size="lg" mb={2} color="blue.600">
                Performance Trends
              </Heading>
              <Text color="gray.600">
                Velocity and acceleration trends over time
              </Text>
            </Box>
            
            <select 
              value={days} 
              onChange={(e) => setDays(Number(e.target.value))}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #E2E8F0',
                backgroundColor: 'white',
                fontSize: '14px'
              }}
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
            </select>
          </HStack>

          {chartLoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" h="300px">
              <VStack gap={2}>
                <Spinner size="lg" color="blue.500" />
                <Text color="gray.600">Loading chart data...</Text>
              </VStack>
            </Box>
          ) : chartData.length > 0 ? (
            <Box>
              <HStack gap={6} mb={4} wrap="wrap" justify="center">
                <HStack gap={2}>
                  <Box w={4} h={4} bg="blue.500" borderRadius="sm"></Box>
                  <Text fontSize="sm" color="gray.600">Velocity (m/s)</Text>
                </HStack>
                <HStack gap={2}>
                  <Box w={4} h={4} bg="orange.500" borderRadius="sm"></Box>
                  <Text fontSize="sm" color="gray.600">Acceleration (m/s²)</Text>
                </HStack>
              </HStack>
              <SimpleLineChart data={chartData} width={800} height={300} />
            </Box>
          ) : (
            <Box bg="gray.50" borderRadius="md" p={8} display="flex" alignItems="center" justifyContent="center" minH="300px">
              <VStack gap={2}>
                <Text color="gray.600">No performance data available for the selected period</Text>
                <Text fontSize="sm" color="gray.500">Try selecting a longer time period (30+ days)</Text>
              </VStack>
            </Box>
          )}
        </VStack>
      </Box>

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