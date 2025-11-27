import { Truck, HardHat, Radio, Users, LayoutDashboard, FileSignature } from "lucide-react";

const nicheApps = [
  {
    title: "Equipment Rental & Inventory",
    description: "Track availability, schedule maintenance, and manage billing for all tools and materials.",
    icon: Truck,
  },
  {
    title: "Safety & Compliance Tracker",
    description: "Log inspections, incidents, and training records with automated compliance reporting.",
    icon: HardHat,
  },
  {
    title: "IoT Real-time Monitoring",
    description: "Integrate site sensors for air quality and location tracking using Django Channels.",
    icon: Radio,
  },
  {
    title: "Construction CRM",
    description: "Manage client profiles, track communications, and streamline proposal workflows.",
    icon: Users,
  },
  {
    title: "Client Progress Portal",
    description: "Secure client access to timelines, photo updates, and project status dashboards.",
    icon: LayoutDashboard,
  },
  {
    title: "Bid Management Platform",
    description: "Streamline the tendering process from project publishing to bid evaluation.",
    icon: FileSignature,
  },
];

export function FeaturesNiche() {
  return (
    <section id="niche" className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-10 pointer-events-none" />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-primary font-mono text-xs tracking-wider uppercase mb-2 block">Specialized Solutions</span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Niche Applications</h2>
          <p className="text-muted-foreground">
            Targeted software solutions addressing specific challenges within the construction lifecycle.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
          {nicheApps.map((app, index) => (
            <div key={index} className="flex gap-4 group">
              <div className="flex-shrink-0 mt-1">
                <div className="h-10 w-10 bg-secondary rounded-sm flex items-center justify-center border border-border group-hover:border-primary/50 transition-colors">
                  <app.icon className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
              </div>
              <div>
                <h3 className="font-display font-bold text-lg mb-2 group-hover:text-primary transition-colors">{app.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed border-l border-border pl-4">
                  {app.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
