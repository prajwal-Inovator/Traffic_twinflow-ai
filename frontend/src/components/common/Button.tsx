import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

type Variant = 'default' | 'secondary' | 'outline' | 'ghost' | 'danger' | string;
type Size = 'sm' | 'md' | 'lg' | string;

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantMap: Record<string, string> = {
  default: 'bg-primary-600 text-white hover:bg-primary-700',
  secondary:
    'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100 hover:bg-slate-300 dark:hover:bg-slate-600',
  outline: 'border border-slate-300 dark:border-slate-600 bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800',
  ghost: 'hover:bg-slate-100 dark:hover:bg-slate-800',
  danger: 'bg-red-600 text-white hover:bg-red-700',
};

const sizeMap: Record<string, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 py-2',
  lg: 'h-12 px-6 text-base',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    const base = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:pointer-events-none disabled:opacity-50';
    const v = variantMap[variant] ?? variantMap.default;
    const s = sizeMap[size] ?? sizeMap.md;
    return <button ref={ref} className={cn(base, v, s, className)} {...props} />;
  }
);
Button.displayName = 'Button';