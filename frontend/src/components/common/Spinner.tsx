import { cn } from '../../utils/cn';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-3',
  lg: 'w-12 h-12 border-4',
};

export const Spinner = ({ size = 'md', className }: SpinnerProps) => (
  <div
    className={cn(
      'inline-block animate-spin rounded-full border-solid border-primary-600 border-t-transparent',
      sizeMap[size],
      className
    )}
    role="status"
  >
    <span className="sr-only">Loading...</span>
  </div>
);