import { AppShell } from "@/components/layout/app-shell";
import { DashboardSkeleton } from "@/components/ui/loading-skeleton";

export default function DashboardLoading() {
  return (
    <AppShell>
      <DashboardSkeleton />
    </AppShell>
  );
}
