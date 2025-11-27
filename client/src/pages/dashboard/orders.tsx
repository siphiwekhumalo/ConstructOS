import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  ShoppingCart, Package, TrendingUp, DollarSign, Search, Plus, 
  ArrowUpRight, ArrowDownLeft, Clock, CheckCircle, Truck
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSalesOrders, getPurchaseOrders, getAccounts, createSalesOrder, createPurchaseOrder } from "@/lib/api";
import { useState } from "react";

export default function DashboardOrders() {
  const queryClient = useQueryClient();
  const [isSalesDialogOpen, setIsSalesDialogOpen] = useState(false);
  const [isPurchaseDialogOpen, setIsPurchaseDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [newSalesOrder, setNewSalesOrder] = useState({
    accountId: "",
    totalAmount: "",
    currency: "USD",
    notes: "",
  });

  const [newPurchaseOrder, setNewPurchaseOrder] = useState({
    supplierId: "",
    totalAmount: "",
    currency: "USD",
    notes: "",
  });

  const { data: salesOrders, isLoading: loadingSales } = useQuery({
    queryKey: ["salesOrders"],
    queryFn: getSalesOrders,
  });

  const { data: purchaseOrders, isLoading: loadingPurchase } = useQuery({
    queryKey: ["purchaseOrders"],
    queryFn: getPurchaseOrders,
  });

  const { data: accounts } = useQuery({
    queryKey: ["accounts"],
    queryFn: getAccounts,
  });

  const createSalesOrderMutation = useMutation({
    mutationFn: createSalesOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["salesOrders"] });
      setIsSalesDialogOpen(false);
      setNewSalesOrder({ accountId: "", totalAmount: "", currency: "USD", notes: "" });
    },
  });

  const createPurchaseOrderMutation = useMutation({
    mutationFn: createPurchaseOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchaseOrders"] });
      setIsPurchaseDialogOpen(false);
      setNewPurchaseOrder({ supplierId: "", totalAmount: "", currency: "USD", notes: "" });
    },
  });

  const totalSalesValue = salesOrders?.reduce((sum, o) => sum + parseFloat(o.totalAmount || "0"), 0) || 0;
  const totalPurchaseValue = purchaseOrders?.reduce((sum, o) => sum + parseFloat(o.totalAmount || "0"), 0) || 0;
  const pendingSalesOrders = salesOrders?.filter(o => o.status === "pending" || o.status === "confirmed").length || 0;
  const pendingPurchaseOrders = purchaseOrders?.filter(o => o.status === "draft" || o.status === "pending").length || 0;

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: "bg-gray-500/20 text-gray-400 border-gray-500/30",
      pending: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      confirmed: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      approved: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      processing: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      shipped: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
      delivered: "bg-green-500/20 text-green-400 border-green-500/30",
      received: "bg-green-500/20 text-green-400 border-green-500/30",
      cancelled: "bg-red-500/20 text-red-400 border-red-500/30",
    };
    return styles[status] || styles.pending;
  };

  const filteredSalesOrders = salesOrders?.filter(order =>
    order.orderNumber?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const filteredPurchaseOrders = purchaseOrders?.filter(order =>
    order.orderNumber?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Order Management
            </h1>
            <p className="text-muted-foreground mt-1">Manage sales orders and procurement.</p>
          </div>
          <div className="flex gap-2">
            <Dialog open={isSalesDialogOpen} onOpenChange={setIsSalesDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2" data-testid="button-add-sales-order">
                  <ArrowUpRight className="h-4 w-4" /> New Sales Order
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-white/10 max-w-md">
                <DialogHeader>
                  <DialogTitle>Create Sales Order</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label>Customer Account</Label>
                    <Select value={newSalesOrder.accountId} onValueChange={(v) => setNewSalesOrder({ ...newSalesOrder, accountId: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-account">
                        <SelectValue placeholder="Select account" />
                      </SelectTrigger>
                      <SelectContent>
                        {accounts?.map(account => (
                          <SelectItem key={account.id} value={account.id}>{account.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Total Amount</Label>
                      <Input
                        placeholder="10000"
                        value={newSalesOrder.totalAmount}
                        onChange={(e) => setNewSalesOrder({ ...newSalesOrder, totalAmount: e.target.value })}
                        className="bg-background border-white/10"
                        data-testid="input-amount"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Currency</Label>
                      <Select value={newSalesOrder.currency} onValueChange={(v) => setNewSalesOrder({ ...newSalesOrder, currency: v })}>
                        <SelectTrigger className="bg-background border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="USD">USD</SelectItem>
                          <SelectItem value="EUR">EUR</SelectItem>
                          <SelectItem value="GBP">GBP</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Input
                      placeholder="Order notes..."
                      value={newSalesOrder.notes}
                      onChange={(e) => setNewSalesOrder({ ...newSalesOrder, notes: e.target.value })}
                      className="bg-background border-white/10"
                    />
                  </div>
                  <Button
                    className="w-full"
                    onClick={() => createSalesOrderMutation.mutate(newSalesOrder as any)}
                    disabled={!newSalesOrder.accountId || !newSalesOrder.totalAmount}
                    data-testid="button-save-sales-order"
                  >
                    Create Sales Order
                  </Button>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={isPurchaseDialogOpen} onOpenChange={setIsPurchaseDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="gap-2 border-white/10" data-testid="button-add-purchase-order">
                  <ArrowDownLeft className="h-4 w-4" /> New Purchase Order
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-white/10 max-w-md">
                <DialogHeader>
                  <DialogTitle>Create Purchase Order</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label>Supplier</Label>
                    <Select value={newPurchaseOrder.supplierId} onValueChange={(v) => setNewPurchaseOrder({ ...newPurchaseOrder, supplierId: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-supplier">
                        <SelectValue placeholder="Select supplier" />
                      </SelectTrigger>
                      <SelectContent>
                        {accounts?.filter(a => a.type === "vendor").map(account => (
                          <SelectItem key={account.id} value={account.id}>{account.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Total Amount</Label>
                      <Input
                        placeholder="5000"
                        value={newPurchaseOrder.totalAmount}
                        onChange={(e) => setNewPurchaseOrder({ ...newPurchaseOrder, totalAmount: e.target.value })}
                        className="bg-background border-white/10"
                        data-testid="input-po-amount"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Currency</Label>
                      <Select value={newPurchaseOrder.currency} onValueChange={(v) => setNewPurchaseOrder({ ...newPurchaseOrder, currency: v })}>
                        <SelectTrigger className="bg-background border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="USD">USD</SelectItem>
                          <SelectItem value="EUR">EUR</SelectItem>
                          <SelectItem value="GBP">GBP</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button
                    className="w-full"
                    onClick={() => createPurchaseOrderMutation.mutate(newPurchaseOrder as any)}
                    disabled={!newPurchaseOrder.supplierId || !newPurchaseOrder.totalAmount}
                    data-testid="button-save-purchase-order"
                  >
                    Create Purchase Order
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Sales Orders</p>
                  <p className="text-2xl font-bold font-display" data-testid="stat-sales-orders">{salesOrders?.length || 0}</p>
                </div>
                <ArrowUpRight className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Sales Value</p>
                  <p className="text-2xl font-bold font-display text-green-500" data-testid="stat-sales-value">${totalSalesValue.toLocaleString()}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Purchase Orders</p>
                  <p className="text-2xl font-bold font-display" data-testid="stat-purchase-orders">{purchaseOrders?.length || 0}</p>
                </div>
                <ArrowDownLeft className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending Processing</p>
                  <p className="text-2xl font-bold font-display text-yellow-500" data-testid="stat-pending">{pendingSalesOrders + pendingPurchaseOrders}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="sales" className="w-full">
          <TabsList className="bg-secondary/50 border border-white/5">
            <TabsTrigger value="sales" className="gap-2" data-testid="tab-sales">
              <ArrowUpRight className="h-4 w-4" /> Sales Orders
            </TabsTrigger>
            <TabsTrigger value="purchase" className="gap-2" data-testid="tab-purchase">
              <ArrowDownLeft className="h-4 w-4" /> Purchase Orders
            </TabsTrigger>
          </TabsList>

          <TabsContent value="sales" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardHeader className="border-b border-white/5">
                <div className="flex items-center gap-4">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search orders..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-background border-white/10"
                      data-testid="input-search"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                  {loadingSales ? (
                    <div className="p-8 text-center text-muted-foreground">Loading sales orders...</div>
                  ) : filteredSalesOrders.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No sales orders found</div>
                  ) : (
                    filteredSalesOrders.map((order) => (
                      <div key={order.id} className="flex items-center gap-4 p-4 hover:bg-white/5" data-testid={`sales-order-row-${order.id}`}>
                        <ShoppingCart className="h-5 w-5 text-green-500" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{order.orderNumber}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(order.orderDate || "").toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${parseFloat(order.totalAmount || "0").toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">{order.currency}</p>
                        </div>
                        <Badge className={getStatusBadge(order.status || "pending")}>
                          {order.status || "pending"}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="purchase" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                  {loadingPurchase ? (
                    <div className="p-8 text-center text-muted-foreground">Loading purchase orders...</div>
                  ) : filteredPurchaseOrders.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No purchase orders found</div>
                  ) : (
                    filteredPurchaseOrders.map((order) => (
                      <div key={order.id} className="flex items-center gap-4 p-4 hover:bg-white/5" data-testid={`purchase-order-row-${order.id}`}>
                        <Package className="h-5 w-5 text-blue-500" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{order.orderNumber}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(order.orderDate || "").toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${parseFloat(order.totalAmount || "0").toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">{order.currency}</p>
                        </div>
                        <Badge className={getStatusBadge(order.status || "draft")}>
                          {order.status || "draft"}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
