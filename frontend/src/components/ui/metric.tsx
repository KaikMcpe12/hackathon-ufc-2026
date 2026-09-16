import { animate, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Card } from "./card";

function useCountUp(value: number, fmt: (n: number) => string) {
  const [txt, setTxt] = useState(() => fmt(value));
  useEffect(() => {
    const controls = animate(0, value, {
      duration: 0.6,
      ease: "easeOut",
      onUpdate: (v) => setTxt(fmt(v)),
    });
    return () => controls.stop();
  }, [value]);
  return txt;
}

export function MetricCard({
  label,
  value,
  format,
  sub,
  ocupacao,
}: {
  label: string;
  value: number;
  format: (n: number) => string;
  sub?: string;
  ocupacao?: number;
}) {
  const txt = useCountUp(value, format);
  const alto = (ocupacao ?? 0) > 0.95;
  return (
    <Card className="p-4">
      <div className="text-xs text-muted">{label}</div>
      <div className="tnum mt-1.5 text-2xl font-extrabold">{txt}</div>
      {sub && <div className="text-xs text-muted">{sub}</div>}
      {ocupacao != null && (
        <>
          <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-neutral-200">
            <motion.div
              className={`h-full rounded-full ${alto ? "bg-brand-500" : "bg-brand"}`}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(100, ocupacao * 100)}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            />
          </div>
          <div className="tnum mt-1 text-right text-xs font-bold">
            {(ocupacao * 100).toFixed(1).replace(".", ",")}%
          </div>
        </>
      )}
    </Card>
  );
}
