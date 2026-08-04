import { BaseChart } from './BaseChart';
import { useMemo } from 'react';

interface CarbonChartProps {
  data: { date: string; co2: number; fuel: number }[];
  title?: string;
}

export const CarbonChart = ({ data, title }: CarbonChartProps) => {
  const option = useMemo(() => ({
    title: {
      text: title || 'Carbon & Fuel Savings',
      textStyle: { fontSize: 14, fontWeight: 'normal' },
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['CO₂ Saved (kg)', 'Fuel Saved (L)'],
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
    },
    yAxis: [
      {
        type: 'value',
        name: 'CO₂ (kg)',
        min: 0,
      },
      {
        type: 'value',
        name: 'Fuel (L)',
        min: 0,
      },
    ],
    series: [
      {
        name: 'CO₂ Saved (kg)',
        type: 'bar',
        data: data.map(d => d.co2),
        color: '#22c55e',
      },
      {
        name: 'Fuel Saved (L)',
        type: 'line',
        yAxisIndex: 1,
        data: data.map(d => d.fuel),
        color: '#f59e0b',
      },
    ],
  }), [data, title]);

  return <BaseChart option={option} />;
};