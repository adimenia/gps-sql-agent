import React, { useEffect, useRef } from 'react';
import { Box } from '@chakra-ui/react';

interface DataPoint {
  x: string;
  velocity: number;
  acceleration: number;
}

interface SimpleLineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
}

const SimpleLineChart: React.FC<SimpleLineChartProps> = ({ 
  data, 
  width = 800, 
  height = 300 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !data || data.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Set up margins
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // Find data ranges
    const velocityValues = data.map(d => d.velocity);
    const accelerationValues = data.map(d => d.acceleration);
    
    const maxVelocity = Math.max(...velocityValues);
    const minVelocity = Math.min(...velocityValues);
    const maxAcceleration = Math.max(...accelerationValues);
    const minAcceleration = Math.min(...accelerationValues);

    // Handle single data point by adding some padding to scales
    const velocityRange = maxVelocity - minVelocity || 1;
    const accelerationRange = maxAcceleration - minAcceleration || 1;
    const velocityPadding = velocityRange * 0.1;
    const accelerationPadding = accelerationRange * 0.1;

    const adjustedMinVelocity = minVelocity - velocityPadding;
    const adjustedMaxVelocity = maxVelocity + velocityPadding;
    const adjustedMinAcceleration = minAcceleration - accelerationPadding;
    const adjustedMaxAcceleration = maxAcceleration + accelerationPadding;

    // Scale functions
    const xScale = (index: number) => {
      if (data.length === 1) return margin.left + chartWidth / 2; // Center single point
      return margin.left + (index / (data.length - 1)) * chartWidth;
    };
    const yScaleVelocity = (value: number) => 
      margin.top + chartHeight - ((value - adjustedMinVelocity) / (adjustedMaxVelocity - adjustedMinVelocity)) * chartHeight;
    const yScaleAcceleration = (value: number) => 
      margin.top + chartHeight - ((value - adjustedMinAcceleration) / (adjustedMaxAcceleration - adjustedMinAcceleration)) * chartHeight;

    // Draw grid lines
    ctx.strokeStyle = '#E2E8F0';
    ctx.lineWidth = 1;
    
    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = margin.top + (i / 5) * chartHeight;
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(margin.left + chartWidth, y);
      ctx.stroke();
    }

    // Vertical grid lines
    for (let i = 0; i <= 5; i++) {
      const x = margin.left + (i / 5) * chartWidth;
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, margin.top + chartHeight);
      ctx.stroke();
    }

    // Draw velocity line
    ctx.strokeStyle = '#3182CE'; // Blue
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((point, index) => {
      const x = xScale(index);
      const y = yScaleVelocity(point.velocity);
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw acceleration line
    ctx.strokeStyle = '#DD6B20'; // Orange
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((point, index) => {
      const x = xScale(index);
      const y = yScaleAcceleration(point.acceleration);
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw data points
    data.forEach((point, index) => {
      const x = xScale(index);
      
      // Velocity points
      const yVel = yScaleVelocity(point.velocity);
      ctx.fillStyle = '#3182CE';
      ctx.beginPath();
      ctx.arc(x, yVel, 4, 0, 2 * Math.PI);
      ctx.fill();
      
      // Acceleration points
      const yAcc = yScaleAcceleration(point.acceleration);
      ctx.fillStyle = '#DD6B20';
      ctx.beginPath();
      ctx.arc(x, yAcc, 4, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Draw axes
    ctx.strokeStyle = '#4A5568';
    ctx.lineWidth = 2;
    
    // Y axis
    ctx.beginPath();
    ctx.moveTo(margin.left, margin.top);
    ctx.lineTo(margin.left, margin.top + chartHeight);
    ctx.stroke();
    
    // X axis
    ctx.beginPath();
    ctx.moveTo(margin.left, margin.top + chartHeight);
    ctx.lineTo(margin.left + chartWidth, margin.top + chartHeight);
    ctx.stroke();

    // Draw labels
    ctx.fillStyle = '#718096';
    ctx.font = '12px system-ui';
    ctx.textAlign = 'center';

    // Y axis labels (velocity scale)
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
      const value = adjustedMinVelocity + (i / 5) * (adjustedMaxVelocity - adjustedMinVelocity);
      const y = margin.top + chartHeight - (i / 5) * chartHeight;
      ctx.fillText(value.toFixed(1), margin.left - 10, y + 4);
    }

    // X axis labels (simplified)
    ctx.textAlign = 'center';
    data.forEach((point, index) => {
      if (index % Math.ceil(data.length / 5) === 0) {
        const x = xScale(index);
        const date = new Date(point.x).toLocaleDateString();
        ctx.fillText(date, x, margin.top + chartHeight + 20);
      }
    });

  }, [data, width, height]);

  return (
    <Box>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          backgroundColor: 'white'
        }}
      />
    </Box>
  );
};

export default SimpleLineChart;