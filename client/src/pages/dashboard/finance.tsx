import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DollarSign, TrendingUp, TrendingDown, CreditCard, PieChart, Plus, FileText, Download } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTransactions, getProjects } from "@/lib/api";
import { useState } from "react";
import { format } from "date-fns";

export default function DashboardFinance() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newTransaction, setNewTransaction] = useState({
    description: "",
    amount: "",
    status: "Pending",
    category: "Materials",
  });

  const { data: transactions, isLoading: txLoading } = useQuery({
    queryKey: ["transactions"],
    queryFn: getTransactions,
  });

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  const createTransaction = useMutation({
    mutationFn: async (data: typeof newTransaction) => {
      const response = await fetch("/api/v1/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: data.description,
          amount: data.amount,
          status: data.status,
          date: new Date(),
        }),
      });
      if (!response.ok) throw new Error("Failed to create transaction");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      setIsDialogOpen(false);
      setNewTransaction({ description: "", amount: "", status: "Pending", category: "Materials" });
    },
  });

  const totalBudget = projects?.reduce((sum, p) => sum + parseFloat(p.budget || "0"), 0) || 0;
  const totalExpenses = transactions?.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0) || 0;
  const remaining = totalBudget - totalExpenses;

  const paidTransactions = transactions?.filter(t => t.status === "Paid") || [];
  const pendingTransactions = transactions?.filter(t => t.status === "Pending") || [];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">Financial Overview</h1>
            <p className="text-muted-foreground mt-1">ERP Finance Module - Track budgets, expenses, and invoices in real-time.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2 border-white/10" data-testid="button-export">
              <Download className="h-4 w-4" /> Export
            </Button>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2" data-testid="button-new-transaction">
                  <Plus className="h-4 w-4" /> New Transaction
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-white/10">
                <DialogHeader>
                  <DialogTitle>Add Transaction</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input
                      placeholder="e.g., Steel Supply Co."
                      value={newTransaction.description}
                      onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-description"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Amount ($)</Label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={newTransaction.amount}
                      onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-amount"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Category</Label>
                      <Select value={newTransaction.category} onValueChange={(v) => setNewTransaction({ ...newTransaction, category: v })}>
                        <SelectTrigger className="bg-background border-white/10" data-testid="select-category">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Materials">Materials</SelectItem>
                          <SelectItem value="Labor">Labor</SelectItem>
                          <SelectItem value="Equipment">Equipment</SelectItem>
                          <SelectItem value="Subcontractor">Subcontractor</SelectItem>
                          <SelectItem value="Overhead">Overhead</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Status</Label>
                      <Select value={newTransaction.status} onValueChange={(v) => setNewTransaction({ ...newTransaction, status: v })}>
                        <SelectTrigger className="bg-background border-white/10" data-testid="select-status">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Pending">Pending</SelectItem>
                          <SelectItem value="Paid">Paid</SelectItem>
                          <SelectItem value="Overdue">Overdue</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button 
                    className="w-full" 
                    onClick={() => createTransaction.mutate(newTransaction)}
                    disabled={!newTransaction.description || !newTransaction.amount}
                    data-testid="button-submit-transaction"
                  >
                    Add Transaction
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Budget</CardTitle>
              <DollarSign className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display" data-testid="text-total-budget">
                ${totalBudget.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Across {projects?.length || 0} projects
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Expenses</CardTitle>
              <TrendingUp className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display" data-testid="text-total-expenses">
                ${totalExpenses.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {transactions?.length || 0} transactions
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Remaining Budget</CardTitle>
              <TrendingDown className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display" data-testid="text-remaining">
                ${remaining.toLocaleString()}
              </div>
              <p className={`text-xs mt-1 ${remaining > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {remaining > 0 ? 'On track' : 'Over budget'}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Pending Payments</CardTitle>
              <CreditCard className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display" data-testid="text-pending">
                {pendingTransactions.length}
              </div>
              <p className="text-xs text-orange-400 mt-1">
                ${pendingTransactions.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0).toLocaleString()} pending
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-white/5 bg-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-primary" /> 
                Budget Utilization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span>Budget Used</span>
                  <span className="font-mono">{totalBudget > 0 ? Math.round((totalExpenses / totalBudget) * 100) : 0}%</span>
                </div>
                <div className="h-3 w-full bg-secondary rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${
                      (totalExpenses / totalBudget) > 0.9 ? 'bg-red-500' :
                      (totalExpenses / totalBudget) > 0.7 ? 'bg-orange-500' : 'bg-primary'
                    }`}
                    style={{ width: `${Math.min((totalExpenses / totalBudget) * 100, 100)}%` }}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4 pt-4">
                  <div className="text-center p-3 bg-secondary/30 rounded-sm">
                    <div className="text-xs text-muted-foreground">Materials</div>
                    <div className="font-mono font-bold mt-1">45%</div>
                  </div>
                  <div className="text-center p-3 bg-secondary/30 rounded-sm">
                    <div className="text-xs text-muted-foreground">Labor</div>
                    <div className="font-mono font-bold mt-1">35%</div>
                  </div>
                  <div className="text-center p-3 bg-secondary/30 rounded-sm">
                    <div className="text-xs text-muted-foreground">Equipment</div>
                    <div className="font-mono font-bold mt-1">20%</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/5 bg-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Payment Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/20 rounded-sm">
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-3 rounded-full bg-green-500" />
                    <span>Paid</span>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold">{paidTransactions.length}</div>
                    <div className="text-xs text-muted-foreground">
                      ${paidTransactions.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-orange-500/10 border border-orange-500/20 rounded-sm">
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-3 rounded-full bg-orange-500" />
                    <span>Pending</span>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold">{pendingTransactions.length}</div>
                    <div className="text-xs text-muted-foreground">
                      ${pendingTransactions.reduce((sum, t) => sum + parseFloat(t.amount || "0"), 0).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/5 bg-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Transactions</CardTitle>
            <Button variant="ghost" size="sm" className="text-primary" data-testid="button-view-all">
              View All
            </Button>
          </CardHeader>
          <CardContent>
            {txLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading transactions...</div>
            ) : transactions && transactions.length > 0 ? (
              <div className="space-y-4">
                {transactions.slice(0, 10).map((tx) => (
                  <div 
                    key={tx.id} 
                    className="flex items-center justify-between p-4 border border-white/5 rounded-sm bg-background hover:border-white/10 transition-colors"
                    data-testid={`row-transaction-${tx.id}`}
                  >
                    <div>
                      <div className="font-bold text-foreground" data-testid={`text-description-${tx.id}`}>
                        {tx.description}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {tx.date ? format(new Date(tx.date), 'MMM dd, yyyy') : 'No date'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono font-bold" data-testid={`text-amount-${tx.id}`}>
                        ${parseFloat(tx.amount).toLocaleString()}
                      </div>
                      <div className={`text-xs font-medium ${
                        tx.status === 'Pending' ? 'text-orange-400' : 
                        tx.status === 'Overdue' ? 'text-red-500' : 'text-green-500'
                      }`} data-testid={`text-status-${tx.id}`}>
                        {tx.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No transactions yet. Add your first transaction to get started.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
