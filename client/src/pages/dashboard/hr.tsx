import { DashboardLayout } from "@/components/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  Users, UserPlus, Calendar, DollarSign, Search, Plus, 
  Clock, CheckCircle, XCircle, FileText, Building 
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getEmployees, getLeaveRequests, getPayrollRecords, createEmployee } from "@/lib/api";
import { useState } from "react";

export default function DashboardHR() {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [newEmployee, setNewEmployee] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    department: "",
    position: "",
    employmentType: "full_time",
    salary: "",
    startDate: "",
  });

  const { data: employees, isLoading: loadingEmployees } = useQuery({
    queryKey: ["employees"],
    queryFn: getEmployees,
  });

  const { data: leaveRequests, isLoading: loadingLeave } = useQuery({
    queryKey: ["leaveRequests"],
    queryFn: getLeaveRequests,
  });

  const { data: payrollRecords } = useQuery({
    queryKey: ["payrollRecords"],
    queryFn: getPayrollRecords,
  });

  const createEmployeeMutation = useMutation({
    mutationFn: createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      setIsDialogOpen(false);
      setNewEmployee({
        firstName: "", lastName: "", email: "", phone: "",
        department: "", position: "", employmentType: "full_time", salary: "", startDate: "",
      });
    },
  });

  const filteredEmployees = employees?.filter(emp =>
    `${emp.firstName} ${emp.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.department?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.position?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const activeEmployees = employees?.filter(e => e.status === "active").length || 0;
  const pendingLeave = leaveRequests?.filter(l => l.status === "pending").length || 0;
  const totalPayroll = payrollRecords?.reduce((sum, p) => sum + parseFloat(p.netPay || "0"), 0) || 0;

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: "bg-green-500/20 text-green-400 border-green-500/30",
      inactive: "bg-gray-500/20 text-gray-400 border-gray-500/30",
      on_leave: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      terminated: "bg-red-500/20 text-red-400 border-red-500/30",
    };
    return styles[status] || styles.inactive;
  };

  const getLeaveStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      approved: "bg-green-500/20 text-green-400 border-green-500/30",
      rejected: "bg-red-500/20 text-red-400 border-red-500/30",
    };
    return styles[status] || styles.pending;
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground" data-testid="text-page-title">
              Human Resources
            </h1>
            <p className="text-muted-foreground mt-1">Manage employees, payroll, and leave requests.</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2" data-testid="button-add-employee">
                <UserPlus className="h-4 w-4" /> Add Employee
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-white/10 max-w-lg">
              <DialogHeader>
                <DialogTitle>Add New Employee</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>First Name</Label>
                    <Input
                      placeholder="John"
                      value={newEmployee.firstName}
                      onChange={(e) => setNewEmployee({ ...newEmployee, firstName: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-first-name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Last Name</Label>
                    <Input
                      placeholder="Smith"
                      value={newEmployee.lastName}
                      onChange={(e) => setNewEmployee({ ...newEmployee, lastName: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-last-name"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      placeholder="john@example.com"
                      value={newEmployee.email}
                      onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-email"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Phone</Label>
                    <Input
                      placeholder="+1 234 567 8900"
                      value={newEmployee.phone}
                      onChange={(e) => setNewEmployee({ ...newEmployee, phone: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-phone"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Department</Label>
                    <Select value={newEmployee.department} onValueChange={(v) => setNewEmployee({ ...newEmployee, department: v })}>
                      <SelectTrigger className="bg-background border-white/10" data-testid="select-department">
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Engineering">Engineering</SelectItem>
                        <SelectItem value="Operations">Operations</SelectItem>
                        <SelectItem value="Finance">Finance</SelectItem>
                        <SelectItem value="HR">HR</SelectItem>
                        <SelectItem value="Safety">Safety</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Position</Label>
                    <Input
                      placeholder="Project Manager"
                      value={newEmployee.position}
                      onChange={(e) => setNewEmployee({ ...newEmployee, position: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-position"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Employment Type</Label>
                    <Select value={newEmployee.employmentType} onValueChange={(v) => setNewEmployee({ ...newEmployee, employmentType: v })}>
                      <SelectTrigger className="bg-background border-white/10">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="full_time">Full Time</SelectItem>
                        <SelectItem value="part_time">Part Time</SelectItem>
                        <SelectItem value="contractor">Contractor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Salary</Label>
                    <Input
                      placeholder="75000"
                      value={newEmployee.salary}
                      onChange={(e) => setNewEmployee({ ...newEmployee, salary: e.target.value })}
                      className="bg-background border-white/10"
                      data-testid="input-salary"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Start Date</Label>
                  <Input
                    type="date"
                    value={newEmployee.startDate}
                    onChange={(e) => setNewEmployee({ ...newEmployee, startDate: e.target.value })}
                    className="bg-background border-white/10"
                    data-testid="input-start-date"
                  />
                </div>
                <Button
                  className="w-full"
                  onClick={() => createEmployeeMutation.mutate(newEmployee as any)}
                  disabled={!newEmployee.firstName || !newEmployee.lastName || !newEmployee.email}
                  data-testid="button-save-employee"
                >
                  Add Employee
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
                  <p className="text-sm text-muted-foreground">Total Employees</p>
                  <p className="text-2xl font-bold font-display" data-testid="stat-total-employees">{employees?.length || 0}</p>
                </div>
                <Users className="h-8 w-8 text-primary opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active</p>
                  <p className="text-2xl font-bold font-display text-green-500" data-testid="stat-active">{activeEmployees}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending Leave</p>
                  <p className="text-2xl font-bold font-display text-yellow-500" data-testid="stat-pending-leave">{pendingLeave}</p>
                </div>
                <Calendar className="h-8 w-8 text-yellow-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-white/5">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Monthly Payroll</p>
                  <p className="text-2xl font-bold font-display" data-testid="stat-payroll">${totalPayroll.toLocaleString()}</p>
                </div>
                <DollarSign className="h-8 w-8 text-primary opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="employees" className="w-full">
          <TabsList className="bg-secondary/50 border border-white/5">
            <TabsTrigger value="employees" className="gap-2" data-testid="tab-employees">
              <Users className="h-4 w-4" /> Employees
            </TabsTrigger>
            <TabsTrigger value="leave" className="gap-2" data-testid="tab-leave">
              <Calendar className="h-4 w-4" /> Leave Requests
            </TabsTrigger>
            <TabsTrigger value="payroll" className="gap-2" data-testid="tab-payroll">
              <DollarSign className="h-4 w-4" /> Payroll
            </TabsTrigger>
          </TabsList>

          <TabsContent value="employees" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardHeader className="border-b border-white/5">
                <div className="flex items-center gap-4">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search employees..."
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
                  {loadingEmployees ? (
                    <div className="p-8 text-center text-muted-foreground">Loading employees...</div>
                  ) : filteredEmployees.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No employees found</div>
                  ) : (
                    filteredEmployees.map((employee) => {
                      const firstName = (employee as any).first_name || employee.firstName || '';
                      const lastName = (employee as any).last_name || employee.lastName || '';
                      return (
                      <div key={employee.id} className="flex items-center gap-4 p-4 hover:bg-white/5" data-testid={`employee-row-${employee.id}`}>
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-primary/20 text-primary">
                            {firstName[0] || '?'}{lastName[0] || '?'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{firstName} {lastName}</p>
                          <p className="text-sm text-muted-foreground">{employee.position || "No position"}</p>
                        </div>
                        <div className="hidden md:block text-sm text-muted-foreground">
                          <Building className="inline h-3 w-3 mr-1" />
                          {employee.department || "N/A"}
                        </div>
                        <Badge className={getStatusBadge(employee.status || "active")}>
                          {employee.status || "active"}
                        </Badge>
                      </div>
                    )})
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leave" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                  {loadingLeave ? (
                    <div className="p-8 text-center text-muted-foreground">Loading leave requests...</div>
                  ) : (leaveRequests?.length || 0) === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No leave requests</div>
                  ) : (
                    leaveRequests?.map((leave) => (
                      <div key={leave.id} className="flex items-center gap-4 p-4 hover:bg-white/5" data-testid={`leave-row-${leave.id}`}>
                        <div className="flex-1">
                          <p className="font-medium capitalize">{leave.type?.replace("_", " ")} Leave</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <Clock className="inline h-3 w-3 mr-1" />
                          {leave.totalDays} days
                        </div>
                        <Badge className={getLeaveStatusBadge(leave.status || "pending")}>
                          {leave.status || "pending"}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="payroll" className="mt-6">
            <Card className="bg-card border-white/5">
              <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                  {(payrollRecords?.length || 0) === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No payroll records</div>
                  ) : (
                    payrollRecords?.map((record) => (
                      <div key={record.id} className="flex items-center gap-4 p-4 hover:bg-white/5" data-testid={`payroll-row-${record.id}`}>
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        <div className="flex-1">
                          <p className="font-medium">Pay Period: {new Date(record.periodStart).toLocaleDateString()} - {new Date(record.periodEnd).toLocaleDateString()}</p>
                          <p className="text-sm text-muted-foreground capitalize">{record.status}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${parseFloat(record.netPay || "0").toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">Net Pay</p>
                        </div>
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
