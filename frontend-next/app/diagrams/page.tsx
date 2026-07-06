"use client";
import { useEffect, useRef, useState } from "react";
import { Loader2, GitGraph, Copy } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { AIThinkingIndicator } from "@/components/ui/loading-skeleton";
import { legacyApi } from "@/lib/api";

const DIAGRAM_TYPES = [
  { value: "flowchart", label: "Architecture Flowchart" },
  { value: "sequence",  label: "Sequence Diagram" },
  { value: "erd",       label: "Entity Relationship (ERD)" },
  { value: "c4",        label: "C4 Context Diagram" },
  { value: "dataflow",  label: "Data Flow Diagram" },
];

const QUICK_EXAMPLES = [
  { topic: "Instagram", summary: "Users upload photos stored in S3, metadata in PostgreSQL, Redis for caching, CDN for delivery." },
  { topic: "Uber",      summary: "Riders request trips, matched with drivers in real-time using geospatial indexing." },
  { topic: "Netflix",   summary: "Video streaming with CDN, microservices for recommendations, billing, and content management." },
];

export default function DiagramsPage() {
  const [topic,    setTopic]    = useState("");
  const [summary,  setSummary]  = useState("");
  const [diagType, setDiagType] = useState("flowchart");
  const [result,   setResult]   = useState<any>(null);
  const [loading,  setLoading]  = useState(false);
  const [elapsed,  setElapsed]  = useState(0);
  const mermaidRef              = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!result?.mermaid_code || !mermaidRef.current) return;
    let cancelled = false;
    import("mermaid").then((m) => {
      if (cancelled) return;
      m.default.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
      const id = `diag-${Date.now()}`;
      m.default.render(id, result.mermaid_code).then(({ svg }) => {
        if (!cancelled && mermaidRef.current) mermaidRef.current.innerHTML = svg;
      }).catch(() => {
        if (!cancelled && mermaidRef.current)
          mermaidRef.current.innerHTML = `<pre class="text-xs text-muted-foreground whitespace-pre-wrap p-4 bg-muted rounded-lg overflow-auto">${result.mermaid_code}</pre>`;
      });
    });
    return () => { cancelled = true; };
  }, [result]);

  const generate = async () => {
    if (!topic.trim() || !summary.trim()) { toast.error("Fill in both fields"); return; }
    setLoading(true); setResult(null); setElapsed(0);
    const start = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);
    try {
      const res = await legacyApi.generateDiagram(topic, summary, diagType);
      setResult(res);
      toast.success("Diagram generated!");
    } catch (err: any) { toast.error(err.message ?? "Failed to generate diagram"); }
    finally { clearInterval(timer); setLoading(false); }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <GitGraph className="h-7 w-7 text-primary" /> Architecture Diagrams
          </h1>
          <p className="text-muted-foreground mt-1">Generate Mermaid diagrams — 5 types supported.</p>
        </div>

        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>System Name</Label>
                <Input placeholder="e.g. Uber, Netflix..." value={topic} onChange={(e) => setTopic(e.target.value)} disabled={loading} />
              </div>
              <div className="space-y-2">
                <Label>Diagram Type</Label>
                <Select value={diagType} onValueChange={setDiagType}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {DIAGRAM_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Design Summary</Label>
              <Textarea rows={3} placeholder="Briefly describe the system components and data flow..." value={summary} onChange={(e) => setSummary(e.target.value)} disabled={loading} />
            </div>
            <Button onClick={generate} disabled={loading} className="w-full gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <GitGraph className="h-4 w-4" />}
              {loading ? `Generating… ${elapsed}s` : "Generate Diagram"}
            </Button>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-muted-foreground self-center">Quick:</span>
              {QUICK_EXAMPLES.map((ex) => (
                <Badge key={ex.topic} variant="secondary"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => { if (!loading) { setTopic(ex.topic); setSummary(ex.summary); } }}>
                  {ex.topic}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {loading && <AIThinkingIndicator message={`Generating ${diagType} diagram for ${topic}…`} />}

        {result && !loading && (
          <div className="space-y-4 animate-fade-in">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{diagType.toUpperCase()} — {topic}</CardTitle>
                  <Button variant="outline" size="sm" onClick={() => { navigator.clipboard.writeText(result.mermaid_code); toast.success("Code copied!"); }} className="gap-1.5">
                    <Copy className="h-3.5 w-3.5" /> Copy Code
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div ref={mermaidRef} className="w-full min-h-[200px] flex items-center justify-center bg-muted/30 rounded-lg p-4 overflow-auto" />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 space-y-3">
                <p className="text-sm">{result.explanation}</p>
                {result.suggestions?.length > 0 && (
                  <ul className="space-y-1.5">
                    {result.suggestions.map((s: string, i: number) => (
                      <li key={i} className="text-sm flex gap-2"><span className="text-primary shrink-0">→</span>{s}</li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
