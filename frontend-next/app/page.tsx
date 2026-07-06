import Link from "next/link";
import { ArrowRight, Cpu, BookOpen, GitGraph, BarChart2, MessageSquare, Star, Zap, Shield, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Navbar } from "@/components/layout/navbar";

const FEATURES = [
  { icon: Cpu,          title: "System Design Generator",  desc: "Generate complete production-grade designs with multi-agent AI." },
  { icon: BookOpen,     title: "Mock Interviews",          desc: "5-round interviews with scoring across 5 dimensions." },
  { icon: Star,         title: "Answer Evaluator",         desc: "Get detailed AI feedback on any system design answer." },
  { icon: GitGraph,     title: "Architecture Diagrams",    desc: "Flowchart, C4, Sequence, ERD, and Data Flow diagrams." },
  { icon: BarChart2,    title: "Performance Analytics",    desc: "Radar charts, trends, and personalised recommendations." },
  { icon: MessageSquare,title: "Coaching Chat",            desc: "Ask anything about system design — context-aware AI coach." },
];

const STATS = [
  { value: "LLaMA 3.3", label: "70B Model" },
  { value: "5",         label: "Diagram Types" },
  { value: "20+",       label: "Topics" },
  { value: "Free",      label: "to Start" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="container pt-20 pb-16 text-center space-y-6">
        <Badge variant="secondary" className="text-xs px-3 py-1">
          <Zap className="h-3 w-3 mr-1" /> Powered by LLaMA 3.3 70B via Groq
        </Badge>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight leading-none">
          Master System Design<br />
          <span className="text-primary">Interviews with AI</span>
        </h1>

        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Generate complete production-grade designs, practice with mock interviews, get scored feedback,
          visualise architectures, and track your improvement — all in one platform.
        </p>

        <div className="flex flex-wrap gap-3 justify-center">
          <Link href="/register">
            <Button size="lg" className="gap-2 px-8 h-12">
              Get Started Free <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/app">
            <Button size="lg" variant="outline" className="gap-2 px-8 h-12">
              Try Without Account
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="flex flex-wrap gap-8 justify-center pt-4">
          {STATS.map(({ value, label }) => (
            <div key={label} className="text-center">
              <div className="text-2xl font-bold text-primary">{value}</div>
              <div className="text-xs text-muted-foreground">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features grid */}
      <section className="container pb-16">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold">Everything you need</h2>
          <p className="text-muted-foreground mt-2">Six powerful features to ace your system design interviews</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <Card key={title} className="group hover:border-primary/50 transition-all duration-200 hover:shadow-md hover:shadow-primary/5">
              <CardContent className="p-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 mb-4 group-hover:bg-primary/20 transition-colors">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold mb-1.5">{title}</h3>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="container pb-20">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-10 text-center space-y-4">
            <h2 className="text-3xl font-bold">Ready to level up?</h2>
            <p className="text-muted-foreground max-w-md mx-auto">
              Join thousands of engineers practising system design with AI coaching.
            </p>
            <div className="flex gap-3 justify-center">
              <Link href="/register">
                <Button size="lg" className="gap-2">
                  Create Free Account <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/app">
                <Button size="lg" variant="outline">Try it now →</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p>© 2026 DesignMentor AI. Built with FastAPI + Next.js + LLaMA 3.3 70B.</p>
          <div className="flex gap-6">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">API Docs</a>
            <Link href="/login" className="hover:text-foreground transition-colors">Sign In</Link>
            <Link href="/design" className="hover:text-foreground transition-colors">Try Now</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
