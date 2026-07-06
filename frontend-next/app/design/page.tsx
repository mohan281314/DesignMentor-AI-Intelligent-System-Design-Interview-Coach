"use client";
import { useState } from "react";
import { Loader2, Download, Sparkles, Cpu, Zap } from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AIThinkingIndicator, DesignSkeleton } from "@/components/ui/loading-skeleton";
import { legacyApi } from "@/lib/api";

const QUICK_TOPICS = [
  "URL Shortener","Twitter / X","Instagram","Netflix",
  "Uber","WhatsApp","YouTube","Distributed Cache",
];

export default function DesignPage() {
  const [topic, setTopic]     = useState("");
  const [design, setDesign]   = useState("");
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  const generate = async (t?: string) => {
    const query = t ?? topic;
    if (!query.trim()) { toast.error("Enter a system name"); return; }
    setLoading(true);
    setDesign("");
    setElapsed(0);

    const start = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);

    try {
      const res = await legacyApi.generateDesign(query);
      setDesign(res.design);
      toast.success("Design generated!");
    } catch (err: any) {
      toast.error(err.message ?? "Generation failed");
    } finally {
      clearInterval(timer);
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Cpu className="h-7 w-7 text-primary" /> System Design Generator
          </h1>
          <p className="text-muted-foreground mt-1">
            Generate complete production-grade system designs powered by LLaMA 3.3 70B.
          </p>
        </div>

        {/* Input */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-2">
              <Input
                placeholder="e.g. Instagram, Netflix, Uber, Twitter..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && generate()}
                className="flex-1"
                disabled={loading}
              />
              <Button onClick={() => generate()} disabled={loading} className="gap-2 px-6">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {loading ? `${elapsed}s…` : "Generate"}
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {QUICK_TOPICS.map((t) => (
                <Badge
                  key={t}
                  variant="secondary"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => { if (!loading) { setTopic(t); generate(t); } }}
                >
                  {t}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Loading */}
        {loading && (
          <div className="space-y-3 animate-fade-in">
            <AIThinkingIndicator
              message={
                elapsed < 3  ? "Analyzing requirements…" :
                elapsed < 7  ? "Designing architecture…" :
                elapsed < 12 ? "Writing API specs and database schema…" :
                               `Almost done… (${elapsed}s)`
              }
            />
            <DesignSkeleton topic={topic} />
          </div>
        )}

        {/* Result */}
        {design && !loading && (
          <Card className="animate-fade-in">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <CardTitle>System Design: {topic}</CardTitle>
                  <CardDescription className="mt-1 flex items-center gap-3">
                    <span>{design.split(" ").length.toLocaleString()} words</span>
                    <span>·</span>
                    <span>~{Math.ceil(design.split(" ").length / 200)} min read</span>
                    <span>·</span>
                    <span className="flex items-center gap-1 text-green-500">
                      <Zap className="h-3 w-3" /> {elapsed}s
                    </span>
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm"
                  onClick={() => { navigator.clipboard.writeText(design); toast.success("Copied!"); }}
                  className="gap-1.5 shrink-0">
                  <Download className="h-3.5 w-3.5" /> Copy
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose-custom">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{design}</ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
