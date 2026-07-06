/**
 * /app — guest-friendly entry point that shows all 6 features
 * without requiring authentication.
 */
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AppShell } from "@/components/layout/app-shell";
import DesignPage from "@/app/design/page";

// We re-export design as default for the /app route; actual tabs
// open their own routes from the navbar. This is a redirect convenience.
import { redirect } from "next/navigation";

export default function GuestApp() {
  redirect("/design");
}
