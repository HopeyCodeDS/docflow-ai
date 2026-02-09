import React from 'react';
import clsx from 'clsx';

interface Column<T> {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  loading?: boolean;
  loadingRows?: React.ReactNode;
  emptyState?: React.ReactNode;
}

function DataTable<T>({
  columns,
  data,
  keyExtractor,
  loading,
  loadingRows,
  emptyState,
}: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200">
            {columns.map((col) => (
              <th
                key={col.key}
                className={clsx(
                  'px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider',
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {loading
            ? loadingRows
            : data.length === 0
            ? (
                <tr>
                  <td colSpan={columns.length}>{emptyState}</td>
                </tr>
              )
            : data.map((row) => (
                <tr
                  key={keyExtractor(row)}
                  className="hover:bg-slate-50 transition-colors"
                >
                  {columns.map((col) => (
                    <td key={col.key} className={clsx('px-4 py-3 text-sm', col.className)}>
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
export type { Column };
