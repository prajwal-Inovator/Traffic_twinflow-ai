import { ReactNode } from 'react';
import { cn } from '../../utils/cn';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}

export const Card = ({ children, className, title, subtitle, actions }: CardProps) => (
  <div
    className={cn(
      'bg-white dark:bg-twinflow-card rounded-xl shadow-md border border-slate-200 dark:border-twinflow-border overflow-hidden',
      className
    )}
  >
    {(title || actions) && (
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-twinflow-border">
        <div>
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center space-x-2">{actions}</div>}
      </div>
    )}
    <div className="px-6 py-4">{children}</div>
  </div>
);