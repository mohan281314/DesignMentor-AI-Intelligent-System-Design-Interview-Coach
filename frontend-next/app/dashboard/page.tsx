"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import {
  BookOpen, Trophy, Cpu, ArrowRight, TrendingUp,
  Star, Target, Zap, Clock,
} from "lucide-react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { analyticsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import { cn, formatScore, scoreToColor } from "@/lib/utils";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) router.push("/login");
  }, [isAuthenticated, router]);

  const { data: perf, isLoading: perfLoading } = useQuery({
    queryKey: ["performance"],
    queryFn: analyticsApi.performance,
    enabled: isAuthenticated,
  });

  const { data: recs } = useQuery({
    queryKey: ["recommendations"],
    queryFn: analyticsApi.recommendations,
    enabled: isAuthenticated,
  });

  const { data: activity } = useQuery({
    queryKey: ["activity"],
    queryFn: () => analyticsApi.activity(8),
    enabled: isAuthenticated,
  });

  const radarData = perf
    ? Object.entries(perf.radar).map(([key, value]) => ({
        dimension: key.charAt(0).toUpperCase() + key.slice(1),
        score: value,
        fullMark: 10,
      }))
    : [];

  const levelColors: Record<string, string> = {
    beginner:     "bg-blue-500/20 text-blue-400",
    intermediate: "bg-yellow-500/20 text-yellow-400",
    advanced:     "bg-orange-500/20 text-orange-400",
    expert:       "bg-green-500/20 text-green-400",
  };

  const activityIcons: Record<string, React.ElementType> = {
    interview_started:  BookOpen,
    interview_completed: Trophy,
    design_generated:   Cpu,
  };

  return (
    <AppShell>
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">
              Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}! 👋
            </h1>
            <p className="text-muted-foreground mt-1">
              Track your progress and keep improving your system design skills.
            </p>
          </div>
          <Link href="/interview">
            <Button className="gap-2">
              <Zap className="h-4 w-4" />
              Start Practice
            </Button>
          </Link>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Overall Score",   value: perf ? formatScore(perf.overall_score) + "/10" : "—", icon: Star,   color: "text-primary" },
            { label: "Interviews",      value: perf?.total_interviews ?? "—",                         icon: BookOpen, color: "text-blue-400" },
            { label: "Designs Saved",   value: perf?.total_designs ?? "—",                            icon: Cpu,    color: "text-purple-400" },
            { label: "Level",           value: perf?.experience_level ?? "—",                         icon: Trophy, color: "text-yellow-400", capitalize: true },
          ].map(({ label, value, icon: Icon, color, capitalize }) => (
            <Card key={label} className="hover:border-primary/50 transition-colors">
              <CardContent className="p-5">
                <Icon className={cn("h-5 w-5 mb-2", color)} />
                <div className={cn("text-2xl font-bold", capitalize && "capitalize")}>{value}</div>
                <div className="text-xs text-muted-foreground mt-0.5">{label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Radar chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Performance Radar</CardTitle>
              <CardDescription>Your strengths across 5 dimensions</CardDescription>
            </CardHeader>
            <CardContent>
              {perfLoading ? (
                <div className="h-56 skeleton rounded-lg" />
              ) : radarData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis dataKey="dimension" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                    <Radar name="Score" dataKey="score" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.25} />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-56 flex flex-col items-center justify-center text-muted-foreground text-sm gap-2">
                  <Target className="h-8 w-8 opacity-40" />
                  <p>Complete an interview to see your radar chart</p>
                  <Link href="/interview"><Button size="sm" variant="outline">Start Interview</Button></Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Trend line chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Score Trend</CardTitle>
              <CardDescription>Your performance over recent interviews</CardDescription>
            </CardHeader>
            <CardContent>
              {perfLoading ? (
                <div className="h-56 skeleton rounded-lg" />
              ) : (perf?.trend ?? []).length > 1 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={perf?.trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="date" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                    <YAxis domain={[0, 10]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8 }} />
                    <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ fill: "hsl(var(--primary))" }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-56 flex flex-col items-center justify-center text-muted-foreground text-sm gap-2">
                  <TrendingUp className="h-8 w-8 opacity-40" />
                  <p>Need 2+ interviews to show trend</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recommendations + Activity */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" /> Recommendations
              </CardTitle>
              <CardDescription>Personalised topics to practise next</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {(recs ?? []).length === 0 ? (
                <p className="text-sm text-muted-foreground">No recommendations yet — start an interview!</p>
              ) : (
                (recs ?? []).map((rec, i) => (
                  <div key={i} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{rec.title}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 truncate">{rec.description}</p>
                    </div>
                    <Link href={`/interview?topic=${encodeURIComponent(rec.topic)}`}>
                      <Button size="icon" variant="ghost" className="h-7 w-7 shrink-0">
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" /> Recent Activity
              </CardTitle>
              <CardDescription>Your latest actions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {(activity ?? []).length === 0 ? (
                <p className="text-sm text-muted-foreground">No activity yet — get started!</p>
              ) : (
                (activity ?? []).map((act: any, i: number) => {
                  const Icon = activityIcons[act.type] ?? BookOpen;
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm truncate">{act.description}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(act.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
