"use client";
import { useState } from "react";
import { Loader2, Star, ClipboardCheck } from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AIThinkingIndicator, EvaluationSkeleton } from "@/components/ui/loading-skeleton";
import { legacyApi } from "@/lib/api";

export default function EvaluatePage() {
  const [question,  setQuestion]  = useState("");
  const [answer,    setAnswer]    = useState("");
  const [reference, setReference] = useState("");
  const [result,    setResult]    = useState("");
  const [loading,   setLoading]   = useState(false);

  const evaluate = async () => {
    if (!question.trim() || !answer.trim()) { toast.error("Question and answer are required"); return; }
    setLoading(true); setResult("");
    try {
      const res = await legacyApi.evaluate(question, answer, reference || undefined);
      setResult(res.evaluation);
      toast.success("Evaluation complete!");
    } catch (err: any) { toast.error(err.message ?? "Evaluation failed"); }
    finally { setLoading(false); }
  };

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-7 w-7 text-primary" /> Answer Evaluator
          </h1>
          <p className="text-muted-foreground mt-1">Get AI feedback scored across 5 dimensions.</p>
        </div>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2">
              <Label>Question</Label>
              <Textarea rows={2} placeholder="e.g. How would you design a URL shortener?" value={question} onChange={(e) => setQuestion(e.target.value)} disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label>Your Answer</Label>
              <Textarea rows={8} placeholder="Describe your system design in detail..." value={answer} onChange={(e) => setAnswer(e.target.value)} disabled={loading} />
              <p className="text-xs text-muted-foreground text-right">{answer.split(" ").filter(Boolean).length} words</p>
            </div>
            <div className="space-y-2">
              <Label>Reference Design <span className="text-muted-foreground font-normal">(optional)</span></Label>
              <Textarea rows={2} placeholder="Paste a reference to compare against..." value={reference} onChange={(e) => setReference(e.target.value)} disabled={loading} />
            </div>
            <Button onClick={evaluate} disabled={loading} className="w-full gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Star className="h-4 w-4" />}
              {loading ? "Evaluating…" : "Evaluate Answer"}
            </Button>
          </CardContent>
        </Card>
        {loading && (
          <div className="space-y-3 animate-fade-in">
            <AIThinkingIndicator message="Scoring your answer across 5 dimensions…" />
            <EvaluationSkeleton />
          </div>
        )}
        {result && !loading && (
          <Card className="animate-fade-in">
            <CardHeader><CardTitle className="text-base flex items-center gap-2"><Star className="h-4 w-4 text-primary" /> Evaluation Result</CardTitle></CardHeader>
            <CardContent>
              <div className="prose-custom"><ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown></div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
