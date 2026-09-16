import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function PageHero({
  title,
  highlight,
  subtitle,
  action,
}: {
  title: string;
  highlight?: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="relative flex items-center justify-between overflow-hidden rounded-2xl px-6 py-8 text-white sm:px-10"
      style={{
        background:
          "radial-gradient(circle at 72% 65%, rgba(255,196,0,.2), transparent 27%), linear-gradient(96deg,#0b0c0e,#25282e)",
      }}
    >
      <span
        aria-hidden
        className="pointer-events-none absolute right-[5%] top-1/2 hidden -translate-y-1/2 select-none text-[150px] font-black tracking-[-18px] text-brand/10 sm:block"
      >
        NL
      </span>
      <div className="relative z-[1] max-w-2xl">
        <h1 className="text-3xl font-extrabold leading-[1.03] tracking-tight sm:text-[42px]">
          {title} {highlight && <span className="text-brand">{highlight}</span>}
        </h1>
        {subtitle && <p className="mt-2 text-neutral-300 sm:text-lg">{subtitle}</p>}
      </div>
      {action && <div className="relative z-[1] hidden sm:block">{action}</div>}
    </motion.section>
  );
}
