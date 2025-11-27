import { Card, CardContent } from "@/components/ui/card";
import { Database, Code2, Map, BrainCircuit, Lock } from "lucide-react";

const techFeatures = [
  {
    title: "Django Admin",
    description: "Auto-generated admin panel for rapid backend data management.",
    icon: Database,
  },
  {
    title: "REST Framework",
    description: "Build powerful APIs for mobile apps and BIM tool integration.",
    icon: Code2,
  },
  {
    title: "GeoDjango",
    description: "Location-based features for equipment tracking and site management.",
    icon: Map,
  },
  {
    title: "Machine Learning",
    description: "Predict delays and optimize resources with Python data libraries.",
    icon: BrainCircuit,
  },
  {
    title: "Enterprise Security",
    description: "Built-in protection against CSRF, XSS, and other common vulnerabilities.",
    icon: Lock,
  },
];

export function TechStack() {
  return (
    <section id="platform" className="py-24 bg-secondary/30 border-y border-border">
      <div className="container mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Powered by Python & Django</h2>
            <p className="text-muted-foreground text-lg mb-8">
              The robust foundation your construction software needs. Scalable, secure, and ready for complex integrations.
            </p>
            
            <div className="space-y-6">
              {techFeatures.map((tech, index) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="mt-1 bg-primary/10 p-2 rounded-sm">
                    <tech.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-display font-bold text-lg">{tech.title}</h4>
                    <p className="text-muted-foreground text-sm">{tech.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-6 shadow-2xl font-mono text-sm relative overflow-hidden">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-transparent" />
             
             {/* Mock Code Block */}
             <div className="space-y-2 text-muted-foreground">
               <div className="flex gap-4 border-b border-border pb-4 mb-4">
                 <div className="w-3 h-3 rounded-full bg-red-500/20" />
                 <div className="w-3 h-3 rounded-full bg-yellow-500/20" />
                 <div className="w-3 h-3 rounded-full bg-green-500/20" />
               </div>

               <p><span className="text-purple-400">from</span> django.contrib.gis.db <span className="text-purple-400">import</span> models</p>
               <p><span className="text-purple-400">from</span> rest_framework <span className="text-purple-400">import</span> serializers</p>
               <br />
               <p><span className="text-blue-400">class</span> <span className="text-yellow-300">ConstructionSite</span>(models.Model):</p>
               <p className="pl-4">name = models.CharField(max_length=<span className="text-orange-400">100</span>)</p>
               <p className="pl-4">location = models.PointField() <span className="text-gray-500"># GeoDjango</span></p>
               <p className="pl-4">budget = models.DecimalField(max_digits=<span className="text-orange-400">12</span>, decimal_places=<span className="text-orange-400">2</span>)</p>
               <p className="pl-4">status = models.CharField(choices=STATUS_CHOICES)</p>
               <br />
               <p><span className="text-blue-400">class</span> <span className="text-yellow-300">SiteSerializer</span>(serializers.ModelSerializer):</p>
               <p className="pl-4"><span className="text-blue-400">class</span> <span className="text-yellow-300">Meta</span>:</p>
               <p className="pl-8">model = ConstructionSite</p>
               <p className="pl-8">fields = <span className="text-green-400">['id', 'name', 'location', 'budget']</span></p>
             </div>

             <div className="absolute bottom-4 right-4 text-xs text-primary animate-pulse">
               ● SERVER CONNECTED
             </div>
          </div>
        </div>
      </div>
    </section>
  );
}
