"""
Shared constants and enums used across all ConstructOS microservices.
"""

USER_ROLES = [
    ('admin', 'Administrator'),
    ('finance', 'Finance User'),
    ('hr', 'HR Manager'),
    ('operations', 'Operations Specialist'),
    ('site_manager', 'Site Manager'),
    ('executive', 'Executive'),
    ('viewer', 'Viewer'),
]

AZURE_AD_ROLES = [
    'Administrator',
    'Finance_User',
    'HR_Manager',
    'Operations_Specialist',
    'Site_Manager',
    'Executive',
]

ACCOUNT_TYPES = [
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
    ('partner', 'Partner'),
    ('prospect', 'Prospect'),
]

ACCOUNT_TIERS = [
    ('enterprise', 'Enterprise'),
    ('mid_market', 'Mid-Market'),
    ('smb', 'Small Business'),
    ('startup', 'Startup'),
]

PAYMENT_TERMS = [
    ('net_15', 'Net 15'),
    ('net_30', 'Net 30'),
    ('net_45', 'Net 45'),
    ('net_60', 'Net 60'),
    ('due_on_receipt', 'Due on Receipt'),
]

LEAD_SOURCES = [
    ('website', 'Website'),
    ('referral', 'Referral'),
    ('trade_show', 'Trade Show'),
    ('cold_call', 'Cold Call'),
    ('social_media', 'Social Media'),
    ('advertisement', 'Advertisement'),
    ('other', 'Other'),
]

LEAD_STATUSES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('qualified', 'Qualified'),
    ('unqualified', 'Unqualified'),
    ('converted', 'Converted'),
]

OPPORTUNITY_STAGES = [
    ('prospecting', 'Prospecting'),
    ('qualification', 'Qualification'),
    ('proposal', 'Proposal'),
    ('negotiation', 'Negotiation'),
    ('closed_won', 'Closed Won'),
    ('closed_lost', 'Closed Lost'),
]

TICKET_PRIORITIES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

TICKET_STATUSES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

PROJECT_STATUSES = [
    ('planning', 'Planning'),
    ('in_progress', 'In Progress'),
    ('on_hold', 'On Hold'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

EMPLOYEE_STATUSES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('on_leave', 'On Leave'),
    ('terminated', 'Terminated'),
]

INVOICE_STATUSES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_METHODS = [
    ('cash', 'Cash'),
    ('check', 'Check'),
    ('credit_card', 'Credit Card'),
    ('bank_transfer', 'Bank Transfer'),
    ('eft', 'EFT'),
]

ORDER_STATUSES = [
    ('draft', 'Draft'),
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

LEAVE_TYPES = [
    ('annual', 'Annual Leave'),
    ('sick', 'Sick Leave'),
    ('unpaid', 'Unpaid Leave'),
    ('maternity', 'Maternity Leave'),
    ('paternity', 'Paternity Leave'),
    ('study', 'Study Leave'),
]

INSPECTION_STATUSES = [
    ('scheduled', 'Scheduled'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

DOCUMENT_CATEGORIES = [
    ('contract', 'Contract'),
    ('invoice', 'Invoice'),
    ('report', 'Report'),
    ('drawing', 'Drawing'),
    ('permit', 'Permit'),
    ('safety', 'Safety'),
    ('other', 'Other'),
]
