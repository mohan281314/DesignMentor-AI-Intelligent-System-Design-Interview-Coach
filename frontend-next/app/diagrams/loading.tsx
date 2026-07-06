import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/loading-skeleton";

export default function DiagramsLoading() {
  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-60" />
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    </AppShell>
  );
}
