import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the API service to avoid network calls in tests
jest.mock('./services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<AppWithRouter />);
    // Just verify the app renders without throwing
    expect(document.body).toBeInTheDocument();
  });

  test('renders navigation links', () => {
    render(<AppWithRouter />);
    
    // Check for main navigation elements
    expect(screen.getByText('🏃‍♂️ Sports Analytics Platform')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Chat Agent')).toBeInTheDocument();
  });
});