import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Upload, Download, Search, FolderOpen, Clock } from "lucide-react";

const documents = [
  {
    id: 1,
    name: "Project_Alpha_Blueprints_v2.pdf",
    type: "Blueprint",
    size: "24.5 MB",
    uploaded: "2 hours ago",
    author: "Architect Team",
  },
  {
    id: 2,
    name: "Site_Safety_Protocol_2025.docx",
    type: "Compliance",
    size: "1.2 MB",
    uploaded: "Yesterday",
    author: "Safety Officer",
  },
  {
    id: 3,
    name: "Q3_Budget_Analysis.xlsx",
    type: "Financial",
    size: "850 KB",
    uploaded: "3 days ago",
    author: "Finance Dept",
  },
  {
    id: 4,
    name: "Vendor_Contracts_Signed.pdf",
    type: "Contract",
    size: "5.6 MB",
    uploaded: "Last week",
    author: "Legal Team",
  },
];

export default function DashboardDocuments() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Document Management</h1>
            <p className="text-muted-foreground mt-1">Secure repository for blueprints, contracts, and reports.</p>
          </div>
          <Button className="gap-2">
            <Upload className="h-4 w-4" /> Upload Document
          </Button>
        </div>

        <div className="flex items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search files..." 
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Folder Structure Mockup */}
          <Card className="md:col-span-1 border-white/5 bg-card h-fit">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Folders</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {['Blueprints', 'Contracts', 'Permits', 'Invoices', 'Safety Reports'].map((folder, i) => (
                <div key={i} className="flex items-center gap-3 p-2 hover:bg-white/5 rounded-sm cursor-pointer transition-colors group">
                  <FolderOpen className="h-4 w-4 text-primary group-hover:text-white transition-colors" />
                  <span className="text-sm font-medium">{folder}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Files Grid */}
          <div className="md:col-span-2 grid gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 bg-card border border-white/5 rounded-sm hover:border-primary/30 transition-all group">
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 bg-secondary rounded-sm flex items-center justify-center">
                    <FileText className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground">{doc.name}</h4>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                      <span>{doc.size}</span>
                      <span>•</span>
                      <span>{doc.author}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right hidden sm:block">
                     <div className="flex items-center gap-1 text-xs text-muted-foreground">
                       <Clock className="h-3 w-3" /> {doc.uploaded}
                     </div>
                  </div>
                  <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
