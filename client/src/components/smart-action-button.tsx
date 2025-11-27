import { Button } from '@/components/ui/button';
import { 
  Edit, 
  ArrowRight, 
  Eye, 
  Send, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Trash2,
  type LucideIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

type EntityType = 'quote' | 'order' | 'ticket' | 'invoice' | 'lead';

interface ActionConfig {
  label: string;
  icon: LucideIcon;
  variant: 'default' | 'secondary' | 'destructive' | 'outline';
  action: string;
}

type StatusActions = Record<string, ActionConfig>;
type EntityActions = Record<EntityType, StatusActions>;

const entityActionMap: EntityActions = {
  quote: {
    draft: { label: 'Edit Quote', icon: Edit, variant: 'default', action: 'edit' },
    pending_approval: { label: 'Approve Quote', icon: CheckCircle, variant: 'default', action: 'approve' },
    approved: { label: 'Convert to Order', icon: ArrowRight, variant: 'default', action: 'convert' },
    sent: { label: 'View Quote', icon: Eye, variant: 'secondary', action: 'view' },
    converted: { label: 'View Sales Order', icon: Eye, variant: 'outline', action: 'view_order' },
    rejected: { label: 'Revise Quote', icon: RefreshCw, variant: 'secondary', action: 'revise' },
  },
  order: {
    draft: { label: 'Edit Order', icon: Edit, variant: 'default', action: 'edit' },
    confirmed: { label: 'Process Order', icon: ArrowRight, variant: 'default', action: 'process' },
    processing: { label: 'Mark Shipped', icon: Send, variant: 'default', action: 'ship' },
    shipped: { label: 'Track Shipment', icon: Eye, variant: 'secondary', action: 'track' },
    delivered: { label: 'View Order', icon: Eye, variant: 'outline', action: 'view' },
    cancelled: { label: 'Reopen Order', icon: RefreshCw, variant: 'secondary', action: 'reopen' },
  },
  ticket: {
    open: { label: 'Start Working', icon: ArrowRight, variant: 'default', action: 'start' },
    in_progress: { label: 'Resolve Ticket', icon: CheckCircle, variant: 'default', action: 'resolve' },
    pending: { label: 'Follow Up', icon: Send, variant: 'secondary', action: 'follow_up' },
    resolved: { label: 'Close Ticket', icon: CheckCircle, variant: 'default', action: 'close' },
    closed: { label: 'Reopen Ticket', icon: RefreshCw, variant: 'secondary', action: 'reopen' },
  },
  invoice: {
    draft: { label: 'Send Invoice', icon: Send, variant: 'default', action: 'send' },
    sent: { label: 'Record Payment', icon: CheckCircle, variant: 'default', action: 'record_payment' },
    paid: { label: 'View Invoice', icon: Eye, variant: 'outline', action: 'view' },
    overdue: { label: 'Send Reminder', icon: Send, variant: 'destructive', action: 'remind' },
    cancelled: { label: 'View Invoice', icon: Eye, variant: 'outline', action: 'view' },
  },
  lead: {
    new: { label: 'Qualify Lead', icon: ArrowRight, variant: 'default', action: 'qualify' },
    contacted: { label: 'Schedule Follow-up', icon: Send, variant: 'default', action: 'follow_up' },
    qualified: { label: 'Convert to Opportunity', icon: ArrowRight, variant: 'default', action: 'convert' },
    converted: { label: 'View Account', icon: Eye, variant: 'outline', action: 'view_account' },
    lost: { label: 'Reactivate Lead', icon: RefreshCw, variant: 'secondary', action: 'reactivate' },
  },
};

interface SmartActionButtonProps {
  entityType: EntityType;
  status: string;
  onAction: (action: string) => void;
  className?: string;
  size?: 'default' | 'sm' | 'lg' | 'icon';
  disabled?: boolean;
}

export function SmartActionButton({ 
  entityType, 
  status, 
  onAction, 
  className,
  size = 'default',
  disabled = false,
}: SmartActionButtonProps) {
  const actions = entityActionMap[entityType];
  const config = actions?.[status];

  if (!config) {
    return (
      <Button 
        variant="outline" 
        size={size}
        className={className}
        disabled
      >
        <Eye className="h-4 w-4 mr-2" />
        View
      </Button>
    );
  }

  const Icon = config.icon;

  return (
    <Button
      variant={config.variant}
      size={size}
      onClick={() => onAction(config.action)}
      className={cn(className)}
      disabled={disabled}
      data-testid={`action-button-${entityType}-${status}`}
    >
      <Icon className="h-4 w-4 mr-2" />
      {config.label}
    </Button>
  );
}

interface ActionButtonGroupProps {
  entityType: EntityType;
  status: string;
  onAction: (action: string) => void;
  showSecondary?: boolean;
  className?: string;
}

export function ActionButtonGroup({ 
  entityType, 
  status, 
  onAction, 
  showSecondary = true,
  className 
}: ActionButtonGroupProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <SmartActionButton 
        entityType={entityType} 
        status={status} 
        onAction={onAction} 
      />
      {showSecondary && (
        <>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => onAction('delete')}
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
            data-testid={`delete-button-${entityType}`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </>
      )}
    </div>
  );
}
