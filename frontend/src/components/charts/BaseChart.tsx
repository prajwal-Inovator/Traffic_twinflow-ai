import ReactECharts from 'echarts-for-react';
import { useUIStore } from '../../store/uiStore';
import { cn } from '../../utils/cn';

interface BaseChartProps {
  option: any;
  className?: string;
  height?: string | number;
  onEvents?: Record<string, Function>;
}

export const BaseChart = ({ option, className, height = 300, onEvents }: BaseChartProps) => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  // Merge theme colors into option
  const finalOption = {
    backgroundColor: 'transparent',
    textStyle: {
      color: isDark ? '#e2e8f0' : '#1e293b',
    },
    ...option,
  };

  return (
    <ReactECharts
      option={finalOption}
      style={{ height, width: '100%' }}
      className={cn(className)}
      theme={isDark ? 'dark' : 'light'}
      onEvents={onEvents}
      opts={{ renderer: 'canvas' }}
    />
  );
};