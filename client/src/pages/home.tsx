import { Navbar } from "@/components/navbar";
import { Hero } from "@/components/hero";
import { FeaturesCMS } from "@/components/features-cms";
import { FeaturesNiche } from "@/components/features-niche";
import { TechStack } from "@/components/tech-stack";
import { CTASection } from "@/components/cta-section";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Hero />
        <FeaturesCMS />
        <TechStack />
        <FeaturesNiche />
        <CTASection />
      </main>
      
      <footer className="py-12 border-t border-border bg-card">
        <div className="container mx-auto px-6 text-center text-muted-foreground text-sm">
          <div className="flex justify-center items-center gap-2 mb-4">
            <div className="h-4 w-4 bg-primary rounded-sm" />
            <span className="font-display font-bold text-foreground">ConstructOS</span>
          </div>
          <p>&copy; 2025 ConstructOS. Powered by Python & Django.</p>
        </div>
      </footer>
    </div>
  );
}
