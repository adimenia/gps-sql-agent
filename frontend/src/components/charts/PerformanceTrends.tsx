import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Text, 
  VStack, 
  HStack,
  Spinner,
  Select,
  Flex
} from '@chakra-ui/react';

interface PerformanceTrendsData {
  date: string;
  avg_velocity: number;
  max_velocity: number;
  avg_acceleration: number;
  max_acceleration: number;
  effort_count: number;
  athlete_count: number;
}

interface PerformanceTrendsResponse {
  chart_data: PerformanceTrendsData[];
  period_days: number;
  group_by: string;
  summary: {
    total_efforts: number;
    unique_athletes: number;
    date_range: {
      start: string;
      end: string;
    };
  };
}

interface PerformanceTrendsProps {
  height?: string;
}

const PerformanceTrends: React.FC<PerformanceTrendsProps> = ({ height = '400px' }) => {
  const [data, setData] = useState<PerformanceTrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(14);
  const [groupBy, setGroupBy] = useState('day');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8001/api/v1/dashboard/charts/performance-trends?days=${days}&group_by=${groupBy}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch performance trends data');
      console.error('Error fetching performance trends:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [days, groupBy]);

  if (loading) {
    return (
      <Box h={height} display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Spinner size="lg" color="blue.500" />
          <Text color="gray.600">Loading performance trends...</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box h={height} display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text color="red.500" fontWeight="bold">Error loading chart</Text>
          <Text color="red.400" fontSize="sm">{error}</Text>
        </VStack>
      </Box>
    );
  }

  if (!data || !data.chart_data || data.chart_data.length === 0) {
    return (
      <Box h={height} display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text color="blue.500" fontWeight="bold">No data available</Text>
          <Text color="gray.600" fontSize="sm">No performance data available for the selected period</Text>
        </VStack>
      </Box>
    );
  }

  const chartData = data.chart_data.map(item => ({
    x: item.date,
    velocity: item.avg_velocity,
    maxVelocity: item.max_velocity,
    acceleration: item.avg_acceleration,
    maxAcceleration: item.max_acceleration,
    efforts: item.effort_count
  }));

  return (
    <Box w="100%" h={height}>
      <VStack gap={4} align="stretch">
        {/* Header with controls */}
        <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
          <VStack align="start" gap={1}>
            <Text fontSize="lg" fontWeight="bold" color="gray.800">
              Performance Trends
            </Text>
            <Text fontSize="sm" color="gray.600">
              Average velocity and acceleration over time
            </Text>
          </VStack>
          
          <HStack gap={3}>
            <Select 
              value={days} 
              onChange={(e) => setDays(Number(e.target.value))}
              size="sm"
              w="auto"
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </Select>
            
            <Select 
              value={groupBy} 
              onChange={(e) => setGroupBy(e.target.value)}
              size="sm"
              w="auto"
            >
              <option value="day">Daily</option>
              <option value="week">Weekly</option>
            </Select>
          </HStack>
        </Flex>

        {/* Summary stats */}
        <HStack gap={6} wrap="wrap">
          <VStack align="start" gap={0}>
            <Text fontSize="sm" color="gray.600">Total Efforts</Text>
            <Text fontSize="lg" fontWeight="bold" color="blue.600">
              {data.summary.total_efforts.toLocaleString()}
            </Text>
          </VStack>
          <VStack align="start" gap={0}>
            <Text fontSize="sm" color="gray.600">Athletes</Text>
            <Text fontSize="lg" fontWeight="bold" color="orange.600">
              {data.summary.unique_athletes}
            </Text>
          </VStack>
          <VStack align="start" gap={0}>
            <Text fontSize="sm" color="gray.600">Period</Text>
            <Text fontSize="lg" fontWeight="bold" color="green.600">
              {data.period_days} days
            </Text>
          </VStack>
        </HStack>

        {/* Chart */}
        <Box flex={1} minH="300px" bg="gray.50" borderRadius="md" display="flex" alignItems="center" justifyContent="center">
          <VStack gap={4}>
            <Text fontSize="lg" fontWeight="bold" color="gray.700">Performance Trends Chart</Text>
            <Text fontSize="sm" color="gray.600">
              Showing {data.summary.total_efforts.toLocaleString()} efforts from {data.summary.unique_athletes} athletes
            </Text>
            <HStack gap={8}>
              <VStack align="center" gap={1}>
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {chartData[0]?.velocity?.toFixed(2) || '0.00'}
                </Text>
                <Text fontSize="sm" color="gray.600">Avg Velocity (m/s)</Text>
              </VStack>
              <VStack align="center" gap={1}>
                <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                  {chartData[0]?.acceleration?.toFixed(2) || '0.00'}
                </Text>
                <Text fontSize="sm" color="gray.600">Avg Acceleration (m/s²)</Text>
              </VStack>
            </HStack>
            <Text fontSize="xs" color="gray.500">Chart visualization coming soon</Text>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default PerformanceTrends;