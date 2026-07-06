/**
 * Reusable loading skeletons for instant visual feedback
 * while AI is generating content.
 */
import { cn } from "@/lib/utils";

// ── Base skeleton block ───────────────────────────────────────────────────────
function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-muted/60",
        className
      )}
      {...props}
    />
  );
}

// ── AI Thinking indicator ─────────────────────────────────────────────────────
export function AIThinkingIndicator({ message = "AI is thinking..." }: { message?: string }) {
  return (
    <div className="flex items-center gap-3 py-4 px-5 rounded-xl border border-primary/20 bg-primary/5">
      {/* Animated dots */}
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-primary animate-bounce"
            style={{ animationDelay: `${i * 0.15}s`, animationDuration: "0.8s" }}
          />
        ))}
      </div>
      <span className="text-sm text-muted-foreground">{message}</span>
    </div>
  );
}

// ── Design output skeleton ────────────────────────────────────────────────────
export function DesignSkeleton({ topic }: { topic: string }) {
  return (
    <div className="rounded-xl border bg-card p-6 space-y-4 animate-fade-in">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
        <span className="text-sm font-medium text-primary">
          Generating system design for <strong>{topic}</strong>…
        </span>
      </div>
      {/* Title skeleton */}
      <Skeleton className="h-7 w-2/3" />
      <Skeleton className="h-4 w-1/3" />
      <div className="border-t border-border pt-4 space-y-3">
        {/* Sections */}
        {[
          { label: "Requirements", width: "90%" },
          { label: "Architecture", width: "75%" },
          { label: "Database Design", width: "85%" },
          { label: "API Design", width: "70%" },
          { label: "Scaling Strategy", width: "80%" },
        ].map(({ label, width }) => (
          <div key={label} className="space-y-2">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-3" style={{ width }} />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3" style={{ width: "60%" }} />
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground text-center pt-2">
        This usually takes 5–15 seconds
      </p>
    </div>
  );
}

// ── Interview question skeleton ───────────────────────────────────────────────
export function QuestionSkeleton() {
  return (
    <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 space-y-2 animate-fade-in">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-5 w-full" />
      <Skeleton className="h-5 w-3/4" />
    </div>
  );
}

// ── Evaluation skeleton ───────────────────────────────────────────────────────
export function EvaluationSkeleton() {
  return (
    <div className="rounded-xl border border-green-500/20 p-4 space-y-3 animate-fade-in">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-6 w-1/3" />
      {[85, 70, 90, 65, 75].map((w, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-3 w-24 shrink-0" />
          <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-primary/40 rounded-full animate-pulse"
              style={{ width: `${w}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Dashboard skeleton ────────────────────────────────────────────────────────
export function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[1,2,3,4].map((i) => (
          <div key={i} className="rounded-xl border bg-card p-5 space-y-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-3 w-20" />
          </div>
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl border bg-card p-6 space-y-3">
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-52 w-full rounded-lg" />
        </div>
        <div className="rounded-xl border bg-card p-6 space-y-3">
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-52 w-full rounded-lg" />
        </div>
      </div>
    </div>
  );
}

export { Skeleton };
