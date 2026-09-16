import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export interface Column<T> {
  key: string;
  header: string;
  align?: "left" | "right";
  render: (row: T) => ReactNode;
}

export function DataTable<T>({
  columns,
  rows,
  footer,
  caption,
  getKey,
  onRowClick,
}: {
  columns: Column<T>[];
  rows: T[];
  footer?: ReactNode[];
  caption?: string;
  getKey: (row: T, i: number) => string;
  onRowClick?: (row: T) => void;
}) {
  return (
    <div className="overflow-auto rounded-xl border border-line">
      <table className="w-full min-w-[680px] border-collapse text-sm">
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead className="bg-neutral-100">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                scope="col"
                className={cn(
                  "whitespace-nowrap px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-muted",
                  c.align === "right" ? "text-right" : "text-left"
                )}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="tnum">
          {rows.map((row, i) => (
            <tr
              key={getKey(row, i)}
              className={cn(
                "border-t border-line transition-colors hover:bg-neutral-50",
                onRowClick && "cursor-pointer focus-within:bg-neutral-50"
              )}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              tabIndex={onRowClick ? 0 : undefined}
              role={onRowClick ? "button" : undefined}
              onKeyDown={
                onRowClick
                  ? (e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onRowClick(row);
                      }
                    }
                  : undefined
              }
            >
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={cn("whitespace-nowrap px-3 py-2.5", c.align === "right" && "text-right")}
                >
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
        {footer && (
          <tfoot>
            <tr className="border-t-2 border-ink bg-neutral-100 font-bold">
              {footer.map((cell, i) => (
                <td
                  key={i}
                  colSpan={i === 0 ? columns.length - (footer.length - 1) : 1}
                  className={cn("px-3 py-2.5", i > 0 && "text-right")}
                >
                  {cell}
                </td>
              ))}
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}
