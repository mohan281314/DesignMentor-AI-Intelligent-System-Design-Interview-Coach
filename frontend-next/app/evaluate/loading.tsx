import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/loading-skeleton";

export default function EvaluateLoading() {
  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-52" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    </AppShell>
  );
}
