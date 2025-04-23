import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number;
  className?: string;
  showPercentage?: boolean;
}

export function Progress({
  value,
  className,
  showPercentage = true,
}: ProgressProps) {
  return (
    <div className="space-y-2">
      <div
        className={cn(
          "h-2 w-full overflow-hidden rounded-full bg-secondary",
          className
        )}
      >
        <div
          className="h-full w-full flex-1 bg-primary transition-all"
          style={{ transform: `translateX(-${100 - value}%)` }}
        />
      </div>
      {showPercentage && (
        <p className="text-sm text-muted-foreground text-right">
          {Math.round(value)}%
        </p>
      )}
    </div>
  );
} 