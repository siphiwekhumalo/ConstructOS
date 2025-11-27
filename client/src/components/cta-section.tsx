import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-24 relative overflow-hidden border-t border-border bg-primary/5">
      <div className="container mx-auto px-6 text-center relative z-10">
        <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Modernize Your Workflow?</h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          Join leading construction firms using our Python & Django powered platform to deliver projects on time and under budget.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/dashboard">
            <Button size="lg" className="rounded-none h-14 px-8 text-lg font-mono">
              SCHEDULE A DEMO <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
          <Button variant="outline" size="lg" className="rounded-none h-14 px-8 text-lg font-mono border-border hover:bg-secondary">
            CONTACT SALES
          </Button>
        </div>
      </div>
      
      {/* Decorative Background */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl" />
      </div>
    </section>
  );
}
