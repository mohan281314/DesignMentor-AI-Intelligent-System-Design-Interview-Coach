import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/loading-skeleton";

export default function ChatLoading() {
  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-52" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="flex flex-col gap-4 h-96">
          {[1,2,3].map(i => (
            <div key={i} className={`flex gap-3 ${i % 2 === 0 ? "flex-row-reverse" : ""}`}>
              <Skeleton className="h-8 w-8 rounded-full shrink-0" />
              <Skeleton className={`h-16 rounded-2xl ${i % 2 === 0 ? "w-2/3" : "w-3/4"}`} />
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
