import { BaseChart } from './BaseChart';
import { useMemo } from 'react';

interface CongestionChartProps {
  data: { timestamp: string; congestion: number }[];
  title?: string;
}

export const CongestionChart = ({ data, title }: CongestionChartProps) => {
  const option = useMemo(() => ({
    title: {
      text: title || 'Congestion Forecast',
      textStyle: { fontSize: 14, fontWeight: 'normal' },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0];
        return `${p.axisValue}<br/>Congestion: ${p.value}%`;
      },
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.timestamp),
      axisLabel: { rotate: 30 },
    },
    yAxis: {
      type: 'value',
      name: 'Congestion (%)',
      min: 0,
      max: 100,
    },
    series: [
      {
        name: 'Congestion',
        type: 'line',
        data: data.map(d => d.congestion),
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 2 },
        areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
    grid: { bottom: 60, top: 50, left: 50, right: 20 },
  }), [data, title]);

  return <BaseChart option={option} />;
};