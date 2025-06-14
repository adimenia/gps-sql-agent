import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Box,
  Flex,
  Heading,
  Container,
  Text,
  Button,
  HStack,
} from '@chakra-ui/react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const bg = 'white'
  const borderColor = 'gray.200'

  return (
    <Box minH="100vh" display="flex" flexDirection="column" bg="gray.50">
      <Box as="nav" bg={bg} borderBottom="1px" borderColor={borderColor} shadow="sm">
        <Container maxW="7xl" py={4}>
          <Flex justify="space-between" align="center">
            <Heading size="lg" color="blue.600">
              🏃‍♂️ Sports Analytics Platform
            </Heading>
            <HStack gap={4}>
              <Button
                as={Link}
                to="/dashboard"
                variant={location.pathname === '/dashboard' || location.pathname === '/' ? 'solid' : 'ghost'}
                colorScheme="blue"
                textDecoration="none"
              >
                Dashboard
              </Button>
              <Button
                as={Link}
                to="/chat"
                variant={location.pathname === '/chat' ? 'solid' : 'ghost'}
                colorScheme="blue"
                textDecoration="none"
              >
                Chat Agent
              </Button>
            </HStack>
          </Flex>
        </Container>
      </Box>
      
      <Box as="main" flex="1" py={8}>
        <Container maxW="7xl">
          {children}
        </Container>
      </Box>
      
      <Box as="footer" borderTop="1px" borderColor={borderColor} py={4} bg={bg}>
        <Container maxW="7xl">
          <Text textAlign="center" color="gray.600">
            &copy; 2024 Sports Analytics Platform. Powered by AI.
          </Text>
        </Container>
      </Box>
    </Box>
  )
}