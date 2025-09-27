import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { CryptoKeyWithScore } from '../types'; // We'll create this types file next

// Define colors for each risk category
const COLORS = {
  Low: '#3dd56d',
  Medium: '#fce83a',
  High: '#ffac33',
  Critical: '#ff4b4b',
};

const getRiskCategory = (score: number | string): keyof typeof COLORS => {
  if (typeof score !== 'number') return 'Low'; // Default for errors/loading
  if (score > 75) return 'Critical';
  if (score > 50) return 'High';
  if (score > 25) return 'Medium';
  return 'Low';
};

interface RiskChartProps {
  keys: CryptoKeyWithScore[];
}

const RiskChart: React.FC<RiskChartProps> = ({ keys }) => {
  // Calculate the count for each risk category
  const data = Object.entries(
    keys.reduce((acc, key) => {
      const category = getRiskCategory(key.vulnerability_score || 0);
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {} as Record<keyof typeof COLORS, number>)
  ).map(([name, value]) => ({ name, value }));

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskChart;