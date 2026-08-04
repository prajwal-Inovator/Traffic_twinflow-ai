import { ReactNode } from 'react';
import { cn } from '../../utils/cn';

interface TableProps {
  headers: string[];
  children: ReactNode;
  className?: string;
}

export const Table = ({ headers, children, className }: TableProps) => (
  <div className={cn('overflow-x-auto', className)}>
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b">
          {headers.map((h) => (
            <th key={h} className="text-left p-2">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  </div>
);