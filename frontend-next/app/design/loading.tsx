import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/loading-skeleton";

export default function DesignLoading() {
  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <div className="flex gap-2">
            <Skeleton className="h-10 flex-1" />
            <Skeleton className="h-10 w-28" />
          </div>
          <div className="flex gap-2 flex-wrap">
            {[1,2,3,4,5,6,7,8].map(i => <Skeleton key={i} className="h-6 w-20 rounded-full" />)}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
