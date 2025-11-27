type EventHandler<T = any> = (event: T) => void | Promise<void>;

interface EventSubscription {
  id: string;
  eventType: string;
  handler: EventHandler;
  serviceName: string;
}

interface Event<T = any> {
  id: string;
  type: string;
  timestamp: Date;
  source: string;
  data: T;
  correlationId?: string;
  metadata?: Record<string, any>;
}

class EventBus {
  private subscriptions: Map<string, EventSubscription[]> = new Map();
  private eventHistory: Event[] = [];
  private maxHistorySize = 1000;

  subscribe<T>(eventType: string, handler: EventHandler<T>, serviceName: string): string {
    const subscriptionId = `${serviceName}-${eventType}-${Date.now()}`;
    const subscription: EventSubscription = {
      id: subscriptionId,
      eventType,
      handler,
      serviceName,
    };

    const existing = this.subscriptions.get(eventType) || [];
    existing.push(subscription);
    this.subscriptions.set(eventType, existing);

    console.log(`[EventBus] ${serviceName} subscribed to ${eventType}`);
    return subscriptionId;
  }

  unsubscribe(subscriptionId: string): boolean {
    const entries = Array.from(this.subscriptions.entries());
    for (const [eventType, subs] of entries) {
      const idx = subs.findIndex((s: EventSubscription) => s.id === subscriptionId);
      if (idx !== -1) {
        subs.splice(idx, 1);
        console.log(`[EventBus] Unsubscribed ${subscriptionId}`);
        return true;
      }
    }
    return false;
  }

  async publish<T>(eventType: string, data: T, source: string, correlationId?: string): Promise<void> {
    const event: Event<T> = {
      id: `evt-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      type: eventType,
      timestamp: new Date(),
      source,
      data,
      correlationId,
    };

    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }

    console.log(`[EventBus] Publishing ${eventType} from ${source}`);

    const handlers = this.subscriptions.get(eventType) || [];
    const wildcardHandlers = this.subscriptions.get("*") || [];
    const allHandlers = [...handlers, ...wildcardHandlers];

    const promises = allHandlers.map(async (sub) => {
      try {
        await Promise.resolve(sub.handler(event));
      } catch (error) {
        console.error(`[EventBus] Error in handler ${sub.serviceName} for ${eventType}:`, error);
      }
    });

    await Promise.all(promises);
  }

  getEventHistory(eventType?: string, limit = 50): Event[] {
    let events = this.eventHistory;
    if (eventType) {
      events = events.filter(e => e.type === eventType);
    }
    return events.slice(-limit);
  }

  getSubscriptions(): { eventType: string; subscribers: string[] }[] {
    const result: { eventType: string; subscribers: string[] }[] = [];
    const entries = Array.from(this.subscriptions.entries());
    for (const [eventType, subs] of entries) {
      result.push({
        eventType,
        subscribers: subs.map((s: EventSubscription) => s.serviceName),
      });
    }
    return result;
  }
}

export const eventBus = new EventBus();

export const EventTypes = {
  LEAD_CREATED: "crm.lead.created",
  LEAD_CONVERTED: "crm.lead.converted",
  LEAD_UPDATED: "crm.lead.updated",
  
  OPPORTUNITY_CREATED: "crm.opportunity.created",
  OPPORTUNITY_WON: "crm.opportunity.won",
  OPPORTUNITY_LOST: "crm.opportunity.lost",
  OPPORTUNITY_UPDATED: "crm.opportunity.updated",
  
  CONTACT_CREATED: "crm.contact.created",
  ACCOUNT_CREATED: "crm.account.created",
  
  TICKET_CREATED: "support.ticket.created",
  TICKET_ASSIGNED: "support.ticket.assigned",
  TICKET_RESOLVED: "support.ticket.resolved",
  TICKET_ESCALATED: "support.ticket.escalated",
  
  CAMPAIGN_LAUNCHED: "marketing.campaign.launched",
  CAMPAIGN_COMPLETED: "marketing.campaign.completed",
  
  INVOICE_CREATED: "finance.invoice.created",
  INVOICE_PAID: "finance.invoice.paid",
  INVOICE_OVERDUE: "finance.invoice.overdue",
  PAYMENT_RECEIVED: "finance.payment.received",
  
  SALES_ORDER_CREATED: "order.sales.created",
  SALES_ORDER_CONFIRMED: "order.sales.confirmed",
  SALES_ORDER_SHIPPED: "order.sales.shipped",
  SALES_ORDER_DELIVERED: "order.sales.delivered",
  
  PURCHASE_ORDER_CREATED: "order.purchase.created",
  PURCHASE_ORDER_APPROVED: "order.purchase.approved",
  PURCHASE_ORDER_RECEIVED: "order.purchase.received",
  
  STOCK_LOW: "inventory.stock.low",
  STOCK_REPLENISHED: "inventory.stock.replenished",
  PRODUCT_CREATED: "inventory.product.created",
  
  EMPLOYEE_HIRED: "hr.employee.hired",
  EMPLOYEE_TERMINATED: "hr.employee.terminated",
  LEAVE_REQUESTED: "hr.leave.requested",
  LEAVE_APPROVED: "hr.leave.approved",
  PAYROLL_PROCESSED: "hr.payroll.processed",
  
  PROJECT_CREATED: "construction.project.created",
  PROJECT_COMPLETED: "construction.project.completed",
  PROJECT_MILESTONE: "construction.project.milestone",
  SAFETY_VIOLATION: "construction.safety.violation",
} as const;

export type EventType = typeof EventTypes[keyof typeof EventTypes];
