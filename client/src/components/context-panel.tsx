import { Link } from 'wouter';
import { 
  Ticket, 
  FileText, 
  User, 
  ChevronRight, 
  Loader2,
  AlertCircle,
  Clock,
  DollarSign
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useAccountRelatedData } from '@/hooks/use-contextual-data';

interface ContextPanelProps {
  accountId: string;
  className?: string;
}

const priorityColors = {
  low: 'bg-slate-500/20 text-slate-400',
  medium: 'bg-amber-500/20 text-amber-400',
  high: 'bg-orange-500/20 text-orange-400',
  urgent: 'bg-red-500/20 text-red-400',
};

const statusColors = {
  open: 'bg-blue-500/20 text-blue-400',
  in_progress: 'bg-amber-500/20 text-amber-400',
  pending: 'bg-purple-500/20 text-purple-400',
  resolved: 'bg-emerald-500/20 text-emerald-400',
  closed: 'bg-slate-500/20 text-slate-400',
  draft: 'bg-slate-500/20 text-slate-400',
  sent: 'bg-blue-500/20 text-blue-400',
  paid: 'bg-emerald-500/20 text-emerald-400',
  overdue: 'bg-red-500/20 text-red-400',
};

function formatCurrency(amount: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(parseFloat(amount));
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

export function ContextPanel({ accountId, className }: ContextPanelProps) {
  const { data, isLoading, error } = useAccountRelatedData(accountId);

  if (isLoading) {
    return (
      <Card className={cn("border-border", className)}>
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("border-border", className)}>
        <CardContent className="p-6 text-center text-muted-foreground">
          <AlertCircle className="h-6 w-6 mx-auto mb-2" />
          <div className="text-sm">Failed to load related data</div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <div className={cn("space-y-4", className)}>
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Ticket className="h-4 w-4 text-purple-400" />
              Open Tickets
            </span>
            <Badge variant="secondary" className="text-xs">
              {data.open_tickets_count}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {data.open_tickets.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              No open tickets
            </div>
          ) : (
            <div className="space-y-2">
              {data.open_tickets.map((ticket) => (
                <Link 
                  key={ticket.id} 
                  href={`/dashboard/support?ticket=${ticket.id}`}
                >
                  <div 
                    className="p-3 rounded-sm bg-secondary/30 hover:bg-secondary cursor-pointer transition-colors group"
                    data-testid={`context-ticket-${ticket.id}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium truncate group-hover:text-primary transition-colors">
                          {ticket.subject}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-muted-foreground">
                            {ticket.ticket_number}
                          </span>
                          <Badge 
                            variant="secondary" 
                            className={cn("text-[10px]", priorityColors[ticket.priority as keyof typeof priorityColors])}
                          >
                            {ticket.priority}
                          </Badge>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center justify-between">
            <span className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-400" />
              Recent Invoices
            </span>
            <Badge variant="secondary" className="text-xs">
              {data.total_invoices}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {data.recent_invoices.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              No invoices
            </div>
          ) : (
            <div className="space-y-2">
              {data.recent_invoices.map((invoice) => (
                <Link 
                  key={invoice.id} 
                  href={`/dashboard/finance?invoice=${invoice.id}`}
                >
                  <div 
                    className="p-3 rounded-sm bg-secondary/30 hover:bg-secondary cursor-pointer transition-colors group"
                    data-testid={`context-invoice-${invoice.id}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            {invoice.invoice_number}
                          </span>
                          <Badge 
                            variant="secondary" 
                            className={cn("text-[10px]", statusColors[invoice.status as keyof typeof statusColors])}
                          >
                            {invoice.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <DollarSign className="h-3 w-3" />
                            {formatCurrency(invoice.total_amount)}
                          </span>
                          {invoice.due_date && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatDate(invoice.due_date)}
                            </span>
                          )}
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center justify-between">
            <span className="flex items-center gap-2">
              <User className="h-4 w-4 text-emerald-400" />
              Contacts
            </span>
            <Badge variant="secondary" className="text-xs">
              {data.total_contacts}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {data.contacts.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              No contacts
            </div>
          ) : (
            <div className="space-y-2">
              {data.contacts.map((contact) => (
                <Link 
                  key={contact.id} 
                  href={`/dashboard/crm?contact=${contact.id}`}
                >
                  <div 
                    className="p-3 rounded-sm bg-secondary/30 hover:bg-secondary cursor-pointer transition-colors group"
                    data-testid={`context-contact-${contact.id}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium group-hover:text-primary transition-colors">
                            {contact.name}
                          </span>
                          {contact.is_primary && (
                            <Badge variant="secondary" className="text-[10px] bg-primary/20 text-primary">
                              Primary
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground mt-0.5">
                          {contact.title && <span>{contact.title} • </span>}
                          {contact.email}
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
