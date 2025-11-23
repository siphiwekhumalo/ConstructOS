import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, TrendingUp, TrendingDown, CreditCard, PieChart } from "lucide-react";

export default function DashboardFinance() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">Financial Overview</h1>
            <p className="text-muted-foreground mt-1">Track budgets, expenses, and invoices in real-time.</p>
          </div>
          <Button className="gap-2">
            <CreditCard className="h-4 w-4" /> New Invoice
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Budget</CardTitle>
              <DollarSign className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display">$12,450,000</div>
              <p className="text-xs text-muted-foreground mt-1">Allocated across 4 active projects</p>
            </CardContent>
          </Card>
          
          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Expenses (YTD)</CardTitle>
              <TrendingUp className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display">$4,230,500</div>
              <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/5">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Remaining</CardTitle>
              <TrendingDown className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-display">$8,219,500</div>
              <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
                On track
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Mock Chart Section */}
        <Card className="border-white/5 bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-primary" /> 
              Expense Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[300px] flex items-center justify-center bg-secondary/20 rounded-sm border border-white/5 border-dashed m-6">
            <p className="text-muted-foreground font-mono text-sm">
              [Chart Visualization Placeholder: Materials vs Labor vs Equipment]
            </p>
          </CardContent>
        </Card>

        <Card className="border-white/5 bg-card">
          <CardHeader>
             <CardTitle>Recent Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { to: "Steel Supply Co.", amount: "$45,000", date: "Today", status: "Pending" },
                { to: "Heavy Machinery Rentals", amount: "$12,500", date: "Yesterday", status: "Paid" },
                { to: "City Concrete Mixers", amount: "$8,200", date: "Oct 24", status: "Paid" },
              ].map((tx, i) => (
                <div key={i} className="flex items-center justify-between p-4 border border-white/5 rounded-sm bg-background">
                   <div>
                     <div className="font-bold text-foreground">{tx.to}</div>
                     <div className="text-xs text-muted-foreground">{tx.date}</div>
                   </div>
                   <div className="text-right">
                     <div className="font-mono font-bold">{tx.amount}</div>
                     <div className={`text-xs font-medium ${tx.status === 'Pending' ? 'text-orange-400' : 'text-green-500'}`}>
                       {tx.status}
                     </div>
                   </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
