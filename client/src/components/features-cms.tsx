import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Calendar, FileText, PieChart, ArrowUpRight } from "lucide-react";

const features = [
  {
    title: "Project Planning & Scheduling",
    description: "Advanced Gantt charts, automated deadline alerts, and seamless calendar integration for precision timeline management.",
    icon: Calendar,
  },
  {
    title: "Document & Drawing Management",
    description: "Centralized repository for blueprints and contracts with robust version control and granular access permissions.",
    icon: FileText,
  },
  {
    title: "Budgeting & Cost Estimation",
    description: "Real-time expense tracking, automated invoicing, and integration with third-party accounting gateways.",
    icon: PieChart,
  },
];

export function FeaturesCMS() {
  return (
    <section id="features" className="py-24 bg-card border-y border-border">
      <div className="container mx-auto px-6">
        <div className="max-w-2xl mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Core Construction <br/> Management System</h2>
          <p className="text-muted-foreground">
            A comprehensive suite of tools designed to manage every aspect of your construction lifecycle with precision and efficiency.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="bg-background border-border hover:border-primary/50 transition-all duration-300 group relative overflow-hidden hover:shadow-lg hover:shadow-primary/5">
              <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowUpRight className="h-5 w-5 text-primary" />
              </div>
              <CardHeader>
                <div className="h-12 w-12 bg-primary/10 rounded-sm flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="font-display text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
