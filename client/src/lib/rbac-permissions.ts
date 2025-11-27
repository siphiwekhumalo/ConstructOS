import { LucideIcon } from "lucide-react";

export type UserRole = 
  | 'system_admin'
  | 'executive'
  | 'finance_manager'
  | 'hr_specialist'
  | 'sales_rep'
  | 'operations_specialist'
  | 'site_manager'
  | 'field_worker'
  | 'warehouse_clerk'
  | 'subcontractor'
  | 'client';

export type NavPermission = 
  | 'dashboard.overview'
  | 'dashboard.projects'
  | 'dashboard.documents'
  | 'dashboard.finance'
  | 'dashboard.equipment'
  | 'dashboard.safety'
  | 'dashboard.iot'
  | 'dashboard.crm'
  | 'dashboard.orders'
  | 'dashboard.hr'
  | 'dashboard.support'
  | 'dashboard.reports'
  | 'dashboard.ai'
  | 'dashboard.chat'
  | 'settings';

export interface NavItem {
  label: string;
  icon: LucideIcon;
  href: string;
  permission: NavPermission;
}

const ROLE_PERMISSIONS: Record<UserRole, NavPermission[]> = {
  system_admin: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.finance',
    'dashboard.equipment',
    'dashboard.safety',
    'dashboard.iot',
    'dashboard.crm',
    'dashboard.orders',
    'dashboard.hr',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.ai',
    'dashboard.chat',
    'settings',
  ],
  
  executive: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.finance',
    'dashboard.equipment',
    'dashboard.safety',
    'dashboard.iot',
    'dashboard.crm',
    'dashboard.orders',
    'dashboard.hr',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.ai',
    'dashboard.chat',
    'settings',
  ],
  
  finance_manager: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.finance',
    'dashboard.orders',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.ai',
    'dashboard.chat',
    'settings',
  ],
  
  hr_specialist: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.hr',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.chat',
    'settings',
  ],
  
  sales_rep: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.crm',
    'dashboard.orders',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.chat',
    'settings',
  ],
  
  operations_specialist: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.equipment',
    'dashboard.safety',
    'dashboard.iot',
    'dashboard.orders',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.chat',
    'settings',
  ],
  
  site_manager: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.equipment',
    'dashboard.safety',
    'dashboard.iot',
    'dashboard.support',
    'dashboard.reports',
    'dashboard.chat',
    'settings',
  ],
  
  field_worker: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.equipment',
    'dashboard.safety',
    'dashboard.support',
    'dashboard.chat',
    'settings',
  ],
  
  warehouse_clerk: [
    'dashboard.overview',
    'dashboard.orders',
    'dashboard.equipment',
    'dashboard.support',
    'dashboard.chat',
    'settings',
  ],
  
  subcontractor: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.safety',
    'dashboard.support',
    'dashboard.chat',
    'settings',
  ],
  
  client: [
    'dashboard.overview',
    'dashboard.projects',
    'dashboard.documents',
    'dashboard.support',
    'dashboard.chat',
    'settings',
  ],
};

export function hasNavPermission(role: string | undefined, permission: NavPermission): boolean {
  if (!role) return false;
  const permissions = ROLE_PERMISSIONS[role as UserRole];
  if (!permissions) return false;
  return permissions.includes(permission);
}

export function getAccessibleNavItems(role: string | undefined, navItems: NavItem[]): NavItem[] {
  if (!role) return [];
  return navItems.filter(item => hasNavPermission(role, item.permission));
}

export function getRolePermissions(role: string | undefined): NavPermission[] {
  if (!role) return [];
  return ROLE_PERMISSIONS[role as UserRole] || [];
}

export const ROLE_DISPLAY_NAMES: Record<UserRole, string> = {
  system_admin: 'System Administrator',
  executive: 'Executive',
  finance_manager: 'Finance Manager',
  hr_specialist: 'HR Specialist',
  sales_rep: 'Sales Representative',
  operations_specialist: 'Operations Specialist',
  site_manager: 'Site Manager',
  field_worker: 'Field Worker',
  warehouse_clerk: 'Warehouse Clerk',
  subcontractor: 'Subcontractor',
  client: 'Client',
};

export const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  system_admin: 'Full access to all system features and settings',
  executive: 'Read-only access to all business data and reports',
  finance_manager: 'Manage invoices, payments, and financial reports',
  hr_specialist: 'Manage employees, payroll, and HR records',
  sales_rep: 'Manage leads, opportunities, and customer relationships',
  operations_specialist: 'Oversee equipment, safety, and operations',
  site_manager: 'Manage assigned construction sites and projects',
  field_worker: 'View assigned projects and submit safety reports',
  warehouse_clerk: 'Manage inventory and stock at assigned warehouse',
  subcontractor: 'View assigned projects and submit work reports',
  client: 'View project progress and communicate with team',
};
