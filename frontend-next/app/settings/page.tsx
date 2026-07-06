"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { Loader2, User, Moon, Sun, Lock } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";

export default function SettingsPage() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { isAuthenticated, user, setUser, logout } = useAuthStore();

  const [fullName, setFullName]     = useState(user?.full_name ?? "");
  const [curPw, setCurPw]           = useState("");
  const [newPw, setNewPw]           = useState("");
  const [saving, setSaving]         = useState(false);
  const [savingPw, setSavingPw]     = useState(false);

  useEffect(() => { if (!isAuthenticated) router.push("/login"); }, [isAuthenticated]);
  useEffect(() => { if (user) setFullName(user.full_name ?? ""); }, [user]);

  const saveProfile = async () => {
    setSaving(true);
    try {
      const updated = await authApi.me();
      setUser(updated);
      toast.success("Profile updated");
    } catch (err: any) {
      toast.error(err.message ?? "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const changePassword = async () => {
    if (!curPw || !newPw) { toast.error("Fill in both password fields"); return; }
    if (newPw.length < 8)  { toast.error("New password must be 8+ characters"); return; }
    setSavingPw(true);
    try {
      await authApi.changePassword(curPw, newPw);
      toast.success("Password changed");
      setCurPw(""); setNewPw("");
    } catch (err: any) {
      toast.error(err.message ?? "Failed to change password");
    } finally {
      setSavingPw(false);
    }
  };

  const handleLogout = () => { logout(); router.push("/login"); };

  return (
    <AppShell>
      <div className="max-w-xl mx-auto space-y-6 animate-fade-in">
        <h1 className="text-2xl font-bold">Settings</h1>

        {/* Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <User className="h-4 w-4 text-primary" /> Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Email</Label>
              <Input value={user?.email ?? ""} disabled className="text-muted-foreground" />
            </div>
            <div className="space-y-2">
              <Label>Full Name</Label>
              <Input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your name" />
            </div>
            <Button onClick={saveProfile} disabled={saving} className="gap-2">
              {saving && <Loader2 className="h-4 w-4 animate-spin" />} Save Profile
            </Button>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              {theme === "dark" ? <Moon className="h-4 w-4 text-primary" /> : <Sun className="h-4 w-4 text-primary" />}
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Button
                variant={theme === "light" ? "default" : "outline"}
                size="sm"
                onClick={() => setTheme("light")}
                className="gap-2"
              >
                <Sun className="h-4 w-4" /> Light
              </Button>
              <Button
                variant={theme === "dark" ? "default" : "outline"}
                size="sm"
                onClick={() => setTheme("dark")}
                className="gap-2"
              >
                <Moon className="h-4 w-4" /> Dark
              </Button>
              <Button
                variant={theme === "system" ? "default" : "outline"}
                size="sm"
                onClick={() => setTheme("system")}
              >
                System
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Password */}
        {user && !user.oauth_provider && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Lock className="h-4 w-4 text-primary" /> Change Password
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input type="password" value={curPw} onChange={(e) => setCurPw(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>New Password</Label>
                <Input type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} placeholder="Min. 8 characters" />
              </div>
              <Button onClick={changePassword} disabled={savingPw} variant="outline" className="gap-2">
                {savingPw && <Loader2 className="h-4 w-4 animate-spin" />} Update Password
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Danger zone */}
        <Card className="border-destructive/30">
          <CardHeader>
            <CardTitle className="text-base text-destructive">Danger Zone</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="destructive" size="sm" onClick={handleLogout}>Sign Out</Button>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
