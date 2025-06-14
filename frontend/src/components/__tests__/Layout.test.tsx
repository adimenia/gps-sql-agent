import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../Layout';

const LayoutWithRouter = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <Layout>{children}</Layout>
  </BrowserRouter>
);

describe('Layout Component', () => {
  test('renders header with title', () => {
    render(
      <LayoutWithRouter>
        <div>Test Content</div>
      </LayoutWithRouter>
    );
    
    expect(screen.getByText('🏃‍♂️ Sports Analytics Platform')).toBeInTheDocument();
  });

  test('renders navigation links', () => {
    render(
      <LayoutWithRouter>
        <div>Test Content</div>
      </LayoutWithRouter>
    );
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Chat Agent')).toBeInTheDocument();
  });

  test('renders children content', () => {
    render(
      <LayoutWithRouter>
        <div>Test Content</div>
      </LayoutWithRouter>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});