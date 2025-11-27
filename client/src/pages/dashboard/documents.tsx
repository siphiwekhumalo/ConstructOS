import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileText, Upload, Download, Search, FolderOpen, Clock, File, FileSpreadsheet, FileImage, Plus, Trash2 } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDocuments, getProjects } from "@/lib/api";
import { useState } from "react";
import { format } from "date-fns";

const folderCategories = ['All Documents', 'Blueprints', 'Contracts', 'Permits', 'Invoices', 'Safety Reports'];

function getFileIcon(type: string) {
  switch (type.toLowerCase()) {
    case 'blueprint':
    case 'drawing':
      return FileImage;
    case 'financial':
    case 'invoice':
      return FileSpreadsheet;
    default:
      return FileText;
  }
}

export default function DashboardDocuments() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFolder, setSelectedFolder] = useState("All Documents");
  const [newDocument, setNewDocument] = useState({
    name: "",
    type: "Contract",
    projectId: "",
    size: "1.2 MB",
    author: "",
  });

  const { data: documents, isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  const createDocument = useMutation({
    mutationFn: async (data: typeof newDocument) => {
      const response = await fetch("/api/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          projectId: data.projectId || null,
          uploadedAt: new Date(),
        }),
      });
      if (!response.ok) throw new Error("Failed to create document");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setIsDialogOpen(false);
      setNewDocument({ name: "", type: "Contract", projectId: "", size: "1.2 MB", author: "" });
    },
  });

  const filteredDocuments = documents?.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.author?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFolder = selectedFolder === "All Documents" || 
                         doc.type?.toLowerCase().includes(selectedFolder.toLowerCase().slice(0, -1));
    return matchesSearch && matchesFolder;
  }) || [];

  const documentStats = {
    total: documents?.length || 0,
    blueprints: documents?.filter(d => d.type === 'Blueprint').length || 0,
    contracts: documents?.filter(d => d.type === 'Contract').length || 0,
    financial: documents?.filter(d => d.type === 'Financial').length || 0,
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Document Management
            </h1>
            <p className="text-muted-foreground mt-1">ERP Document Repository - Secure storage for blueprints, contracts, and reports.</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-upload">
                <Upload className="h-4 w-4" /> Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10">
              <DialogHeader>
                <DialogTitle>Upload Document</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label>Document Name</Label>
                  <Input
                    placeholder="e.g., Project_Alpha_Blueprint.pdf"
                    value={newDocument.name}
                    onChange={(e) => setNewDocument({ ...newDocument, name: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Document Type</Label>
                    <Select value={newDocument.type} onValueChange={(v) => setNewDocument({ ...newDocument, type: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Blueprint">Blueprint</SelectItem>
                        <SelectItem value="Contract">Contract</SelectItem>
                        <SelectItem value="Permit">Permit</SelectItem>
                        <SelectItem value="Invoice">Invoice</SelectItem>
                        <SelectItem value="Financial">Financial</SelectItem>
                        <SelectItem value="Compliance">Compliance</SelectItem>
                        <SelectItem value="Safety">Safety Report</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Related Project</Label>
                    <Select value={newDocument.projectId} onValueChange={(v) => setNewDocument({ ...newDocument, projectId: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-project">
                        <SelectValue placeholder="Select project" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {projects?.map(p => (
                          <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Author / Uploaded By</Label>
                  <Input
                    placeholder="e.g., Architect Team"
                    value={newDocument.author}
                    onChange={(e) => setNewDocument({ ...newDocument, author: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-author"
                  />
                </div>
                <Button 
                  className="w-full" 
                  onClick={() => createDocument.mutate(newDocument)}
                  disabled={!newDocument.name}
                  data-testid="button-submit"
                >
                  Upload Document
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Documents</p>
                  <p className="text-2xl font-bold font-display mt-1" data-testid="stat-total">
                    {documentStats.total}
                  </p>
                </div>
                <File className="h-8 w-8 text-primary opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Blueprints</p>
                  <p className="text-2xl font-bold font-display mt-1">{documentStats.blueprints}</p>
                </div>
                <FileImage className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Contracts</p>
                  <p className="text-2xl font-bold font-display mt-1">{documentStats.contracts}</p>
                </div>
                <FileText className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Financial</p>
                  <p className="text-2xl font-bold font-display mt-1">{documentStats.financial}</p>
                </div>
                <FileSpreadsheet className="h-8 w-8 text-orange-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex items-center gap-4 bg-card p-4 rounded-sm border border-white/5">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search files by name or author..." 
              className="pl-9 bg-background border-white/10 focus-visible:ring-primary"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              data-testid="input-search"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          <Card className="md:col-span-1 border-white/5 bg-card h-fit">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Folders</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {folderCategories.map((folder, i) => (
                <div 
                  key={i} 
                  className={`flex items-center gap-3 p-2 rounded-sm cursor-pointer transition-colors ${
                    selectedFolder === folder ? 'bg-primary/20 text-primary' : 'hover:bg-white/5'
                  }`}
                  onClick={() => setSelectedFolder(folder)}
                  data-testid={`folder-${folder.toLowerCase().replace(' ', '-')}`}
                >
                  <FolderOpen className={`h-4 w-4 ${selectedFolder === folder ? 'text-primary' : 'text-muted-foreground'}`} />
                  <span className="text-sm font-medium">{folder}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="md:col-span-3">
            {isLoading ? (
              <div className="text-center py-12 text-muted-foreground">Loading documents...</div>
            ) : filteredDocuments.length > 0 ? (
              <div className="grid gap-4">
                {filteredDocuments.map((doc) => {
                  const FileIcon = getFileIcon(doc.type || '');
                  return (
                    <div 
                      key={doc.id} 
                      className="flex items-center justify-between p-4 bg-card border border-white/5 rounded-sm hover:border-primary/30 transition-all group"
                      data-testid={`doc-${doc.id}`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-10 w-10 bg-secondary rounded-sm flex items-center justify-center">
                          <FileIcon className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                        <div>
                          <h4 className="font-medium text-foreground" data-testid={`doc-name-${doc.id}`}>
                            {doc.name}
                          </h4>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                            <span className="px-2 py-0.5 bg-secondary rounded text-xs">{doc.type}</span>
                            <span>{doc.size}</span>
                            <span>•</span>
                            <span>{doc.author}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="text-right hidden sm:block">
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" /> 
                            {doc.uploadedAt ? format(new Date(doc.uploadedAt), 'MMM dd, yyyy') : 'Unknown'}
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                          data-testid={`download-${doc.id}`}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground border border-dashed border-white/10 rounded-sm">
                {searchTerm || selectedFolder !== "All Documents" 
                  ? "No documents match your search criteria."
                  : "No documents uploaded yet. Upload your first document to get started."}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
