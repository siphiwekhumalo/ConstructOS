import { Button } from "@/components/ui/button";
import { ArrowRight, ShieldCheck, Cpu, Activity } from "lucide-react";
import heroImage from "@assets/generated_images/futuristic_construction_site_with_digital_overlay.png";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden border-b border-white/5">
      {/* Grid Background */}
      <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none" />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              <span className="text-xs font-mono text-primary tracking-wider">SYSTEM OPERATIONAL</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
              <span className="text-gradient">Future-Proof</span> <br />
              <span className="text-gradient-primary">Construction Tech</span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-xl leading-relaxed">
              Leverage the power of Python and Django to build robust, scalable, and secure software solutions tailored for the modern construction industry.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="rounded-none h-12 px-8 font-mono text-sm">
                START BUILDING <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button variant="outline" size="lg" className="rounded-none h-12 px-8 font-mono text-sm border-white/10 hover:bg-white/5">
                VIEW DOCUMENTATION
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-8 pt-8 border-t border-white/5">
              <div>
                <div className="flex items-center gap-2 mb-2 text-primary">
                  <ShieldCheck className="h-5 w-5" />
                  <span className="font-mono text-xs font-bold">SECURE</span>
                </div>
                <p className="text-xs text-muted-foreground">Enterprise-grade protection</p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2 text-primary">
                  <Cpu className="h-5 w-5" />
                  <span className="font-mono text-xs font-bold">SCALABLE</span>
                </div>
                <p className="text-xs text-muted-foreground">Built for growth</p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2 text-primary">
                  <Activity className="h-5 w-5" />
                  <span className="font-mono text-xs font-bold">ROBUST</span>
                </div>
                <p className="text-xs text-muted-foreground">99.9% Uptime architecture</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="aspect-video rounded-sm overflow-hidden border border-white/10 shadow-2xl relative group">
              <div className="absolute inset-0 bg-primary/10 mix-blend-overlay group-hover:bg-transparent transition-colors duration-500" />
              <img 
                src={heroImage} 
                alt="Futuristic Construction Site" 
                className="w-full h-full object-cover scale-105 group-hover:scale-100 transition-transform duration-700"
              />
              
              {/* UI Overlay Elements */}
              <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md border border-white/10 p-4 rounded-sm max-w-[200px]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-mono text-muted-foreground">STATUS</span>
                  <span className="text-[10px] font-mono text-green-500">ACTIVE</span>
                </div>
                <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[75%]" />
                </div>
              </div>

              <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md border border-white/10 p-4 rounded-sm">
                 <div className="text-[10px] font-mono text-primary mb-1">IoT SENSORS</div>
                 <div className="text-lg font-bold font-display">Zone A: Optimal</div>
              </div>
            </div>
            
            {/* Decorative Elements behind */}
            <div className="absolute -z-10 -bottom-4 -right-4 w-full h-full border border-primary/20 rounded-sm" />
            <div className="absolute -z-10 -top-4 -left-4 w-full h-full border border-white/5 rounded-sm" />
          </div>
        </div>
      </div>
    </section>
  );
}
