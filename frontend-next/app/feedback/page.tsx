"use client";
import { useState } from "react";
import { Loader2, BookOpen } from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AIThinkingIndicator } from "@/components/ui/loading-skeleton";
import { legacyApi } from "@/lib/api";

const POPULAR = ["Netflix","Instagram","Uber","Twitter","WhatsApp","YouTube","Dropbox"];

export default function FeedbackPage() {
  const [topic,     setTopic]     = useState("");
  const [sessionId, setSessionId] = useState("");
  const [report,    setReport]    = useState("");
  const [loading,   setLoading]   = useState(false);
  const [elapsed,   setElapsed]   = useState(0);

  const generate = async (t?: string) => {
    const q = t ?? topic;
    if (!q.trim()) { toast.error("Enter a topic"); return; }
    setLoading(true); setReport(""); setElapsed(0);
    const start = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);
    try {
      const res = await legacyApi.generateFeedback(q, sessionId || undefined);
      setReport(res.report);
      toast.success("Learning report generated!");
    } catch (err: any) { toast.error(err.message ?? "Failed to generate report"); }
    finally { clearInterval(timer); setLoading(false); }
  };

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="h-7 w-7 text-primary" /> Learning Report
          </h1>
          <p className="text-muted-foreground mt-1">Personalised post-interview feedback with resources and tips.</p>
        </div>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2">
              <Label>Topic</Label>
              <Input placeholder="e.g. Netflix, Instagram, Uber..." value={topic} onChange={(e) => setTopic(e.target.value)} onKeyDown={(e) => e.key === "Enter" && generate()} disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label>Session ID <span className="text-muted-foreground font-normal">(optional)</span></Label>
              <Input placeholder="Paste session ID from your interview..." value={sessionId} onChange={(e) => setSessionId(e.target.value)} disabled={loading} />
            </div>
            <Button onClick={() => generate()} disabled={loading} className="w-full gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <BookOpen className="h-4 w-4" />}
              {loading ? `Generating… ${elapsed}s` : "Generate Report"}
            </Button>
            <div className="flex flex-wrap gap-2">
              {POPULAR.map((t) => (
                <Badge key={t} variant="secondary"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => { if (!loading) { setTopic(t); generate(t); } }}>
                  {t}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
        {loading && <AIThinkingIndicator message={`Generating learning report for ${topic}…`} />}
        {report && !loading && (
          <Card className="animate-fade-in">
            <CardHeader><CardTitle className="text-base">Learning Report: {topic}</CardTitle></CardHeader>
            <CardContent>
              <div className="prose-custom"><ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown></div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
