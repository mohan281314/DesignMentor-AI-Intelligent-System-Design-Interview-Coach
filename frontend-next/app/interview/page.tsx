"use client";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Loader2, ChevronRight, RotateCcw, BookOpen, Trophy, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AIThinkingIndicator, QuestionSkeleton, EvaluationSkeleton } from "@/components/ui/loading-skeleton";
import { legacyApi } from "@/lib/api";

type Phase = "setup" | "active" | "complete";
interface Turn { question: string; answer: string; evaluation: string; }

const MAX_TURNS = 5;
const QUICK_TOPICS = [
  "URL Shortener","Twitter","Netflix","Uber","Instagram","WhatsApp","YouTube","Dropbox",
];

export default function InterviewPage() {
  const searchParams                  = useSearchParams();
  const defaultTopic                  = searchParams.get("topic") ?? "";
  const [phase,     setPhase]         = useState<Phase>("setup");
  const [topic,     setTopic]         = useState(defaultTopic);
  const [sessionId, setSessionId]     = useState<string | undefined>();
  const [question,  setQuestion]      = useState("");
  const [answer,    setAnswer]        = useState("");
  const [turns,     setTurns]         = useState<Turn[]>([]);
  const [loading,   setLoading]       = useState(false);
  const [loadType,  setLoadType]      = useState<"start"|"eval"|"next">("start");
  const [turnNum,   setTurnNum]       = useState(0);
  const bottomRef                     = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [turns]);
  useEffect(() => { if (defaultTopic) startInterview(defaultTopic); }, []); // eslint-disable-line

  const startInterview = async (t?: string) => {
    const target = t ?? topic;
    if (!target.trim()) { toast.error("Enter a topic"); return; }
    setLoading(true); setLoadType("start");
    try {
      const res = await legacyApi.startInterview(target);
      setSessionId(res.session_id);
      setQuestion(res.first_question);
      setTurns([]); setTurnNum(1); setPhase("active");
    } catch (err: any) { toast.error(err.message ?? "Could not start interview"); }
    finally { setLoading(false); }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !sessionId) return;
    setLoading(true); setLoadType("eval");
    const currentQ = question;
    const currentA = answer;
    setAnswer("");
    try {
      const res = await legacyApi.submitAnswer(sessionId, currentA);
      setTurns((prev) => [...prev, { question: currentQ, answer: currentA, evaluation: res.evaluation }]);
      if (res.is_complete) {
        setPhase("complete");
        toast.success("Interview complete!");
      } else {
        setLoadType("next");
        setQuestion(res.next_question ?? "");
        setTurnNum((n) => n + 1);
      }
    } catch (err: any) { toast.error(err.message ?? "Submission failed"); }
    finally { setLoading(false); }
  };

  const reset = () => { setPhase("setup"); setTurns([]); setQuestion(""); setAnswer(""); setSessionId(undefined); setTurnNum(0); };

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="h-7 w-7 text-primary" /> Mock Interview
          </h1>
          <p className="text-muted-foreground mt-1">Answer up to {MAX_TURNS} questions with real-time AI evaluation.</p>
        </div>

        {/* Setup */}
        {phase === "setup" && (
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="flex gap-2">
                <Input placeholder="e.g. Netflix, Uber, WhatsApp..." value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && startInterview()} disabled={loading} />
                <Button onClick={() => startInterview()} disabled={loading} className="gap-2">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ChevronRight className="h-4 w-4" />}
                  {loading ? "Starting…" : "Start"}
                </Button>
              </div>
              {loading && <AIThinkingIndicator message="Preparing your interview question…" />}
              <div className="flex flex-wrap gap-2">
                {QUICK_TOPICS.map((t) => (
                  <Badge key={t} variant="secondary"
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                    onClick={() => { if (!loading) { setTopic(t); startInterview(t); } }}>
                    {t}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Active */}
        {(phase === "active" || phase === "complete") && (
          <>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="outline">{topic}</Badge>
                <span className="text-sm text-muted-foreground">
                  {phase === "complete" ? "Complete" : `Q${turnNum} of ${MAX_TURNS}`}
                </span>
              </div>
              <Button variant="ghost" size="sm" onClick={reset} className="gap-1.5">
                <RotateCcw className="h-3.5 w-3.5" /> New
              </Button>
            </div>
            <Progress value={(turnNum / MAX_TURNS) * 100} />

            {/* Past turns */}
            {turns.map((turn, i) => (
              <div key={i} className="space-y-3">
                <Card className="border-muted">
                  <CardContent className="pt-4 pb-4">
                    <p className="text-xs text-muted-foreground mb-1 font-medium uppercase tracking-wider">Question {i + 1}</p>
                    <p className="text-sm font-medium">{turn.question}</p>
                  </CardContent>
                </Card>
                <Card className="border-primary/20 bg-primary/5">
                  <CardContent className="pt-4 pb-4">
                    <p className="text-xs text-muted-foreground mb-1 font-medium uppercase tracking-wider">Your Answer</p>
                    <p className="text-sm whitespace-pre-wrap">{turn.answer}</p>
                  </CardContent>
                </Card>
                <Card className="border-green-500/30">
                  <CardContent className="pt-4 pb-4">
                    <p className="text-xs text-muted-foreground mb-2 font-medium uppercase tracking-wider">Evaluation</p>
                    <div className="prose-custom text-sm">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{turn.evaluation}</ReactMarkdown>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}

            {/* Evaluation loading */}
            {loading && loadType === "eval" && (
              <div className="space-y-3 animate-fade-in">
                <AIThinkingIndicator message="Evaluating your answer…" />
                <EvaluationSkeleton />
              </div>
            )}

            {/* Next question loading */}
            {loading && loadType === "next" && (
              <div className="space-y-2 animate-fade-in">
                <AIThinkingIndicator message="Preparing next question…" />
                <QuestionSkeleton />
              </div>
            )}

            {/* Current question */}
            {phase === "active" && !loading && (
              <div className="space-y-3">
                <Card className="border-primary/50">
                  <CardContent className="pt-4 pb-4">
                    <p className="text-xs text-muted-foreground mb-1 font-medium uppercase tracking-wider">Question {turnNum}</p>
                    <p className="text-sm font-medium">{question}</p>
                  </CardContent>
                </Card>
                <div className="space-y-2">
                  <Textarea rows={6} placeholder="Type your answer here — be as detailed as possible…"
                    value={answer} onChange={(e) => setAnswer(e.target.value)} className="resize-none" />
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">{answer.split(" ").filter(Boolean).length} words</span>
                    <Button onClick={submitAnswer} disabled={!answer.trim()} className="gap-2">
                      <Send className="h-4 w-4" /> Submit Answer
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Complete */}
            {phase === "complete" && (
              <Card className="border-primary bg-primary/10">
                <CardContent className="pt-6 pb-6 text-center space-y-3">
                  <Trophy className="h-10 w-10 text-primary mx-auto" />
                  <h3 className="text-xl font-bold">Interview Complete! 🎉</h3>
                  <p className="text-muted-foreground text-sm">You answered all {turns.length} questions. Review your evaluations above.</p>
                  <div className="flex gap-3 justify-center">
                    <Button onClick={reset} variant="outline" className="gap-2"><RotateCcw className="h-4 w-4" /> New Interview</Button>
                    <Button asChild><a href="/dashboard">View Progress</a></Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
        <div ref={bottomRef} />
      </div>
    </AppShell>
  );
}
