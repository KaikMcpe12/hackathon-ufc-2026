import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl font-bold transition-all active:scale-[.98] disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        yellow: "bg-brand text-ink hover:brightness-95",
        dark: "bg-ink text-white hover:bg-ink/90",
        light: "bg-neutral-100 text-ink border border-line hover:bg-neutral-200",
        ghost: "text-ink hover:bg-neutral-100",
      },
      size: { md: "h-11 px-5 text-sm", sm: "h-9 px-3 text-sm", icon: "h-10 w-10" },
    },
    defaultVariants: { variant: "yellow", size: "md" },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({ className, variant, size, asChild, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
