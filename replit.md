# ConstructOS - Construction Management Platform

## Overview

ConstructOS is a comprehensive construction management system built with Python, Django, TypeScript, and React. The application provides a full-stack solution for managing construction projects, equipment, safety inspections, finances, documents, and client relationships. It leverages modern web technologies including shadcn/ui components, Tailwind CSS, and a PostgreSQL database.

The platform is designed to modernize construction workflows with features spanning project planning, equipment tracking, safety compliance, IoT monitoring, CRM capabilities, and analytics reporting.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:**
- React 18+ with TypeScript for type safety
- Vite as the build tool and development server
- Wouter for client-side routing (lightweight alternative to React Router)
- TanStack Query (React Query) for server state management and caching
- shadcn/ui component library built on Radix UI primitives
- Tailwind CSS v4 for styling with custom CSS variables

**Design Decisions:**
- **Component Library**: Uses shadcn/ui (New York variant) for consistent, accessible UI components. This provides pre-built components that can be customized while maintaining accessibility standards through Radix UI.
- **State Management**: TanStack Query handles all server state with aggressive caching (staleTime: Infinity), reducing unnecessary network requests. Client state is managed through React hooks.
- **Routing**: Wouter provides a minimal routing solution (~1KB) compared to React Router, suitable for the application's routing needs.
- **Styling Approach**: Tailwind CSS with CSS variables for theming, allowing runtime theme switching. Custom fonts (Inter, Space Grotesk, JetBrains Mono) for typography hierarchy.

### Backend Architecture

**Technology Stack:**
- Python 3.11 with Django 5.2
- Django REST Framework for API development
- Gunicorn (production WSGI server) with 4 workers and gthread worker class
- Express.js as API gateway/proxy (port 5000)
- Django backend (port 8000)

**Design Decisions:**
- **API Structure**: RESTful API design with versioned `/api/v1` endpoints. Django handles all business logic and database operations.
- **Proxy Architecture**: Express serves as an API gateway, proxying `/api/v1/*` requests to Django while serving the React frontend via Vite.
- **Production Server**: Gunicorn serves Django in production with 4 workers and 2 threads each for better concurrency. Enable via `USE_GUNICORN=true` environment variable.
- **Development Setup**: Express spawns Django (dev server or Gunicorn) as a child process for unified development workflow. Both servers start with a single `npm run dev` command.
- **Request Logging**: Custom middleware logs API requests with timing, method, path, and status codes.

**Environment Variables:**
- `USE_GUNICORN=true` - Enable Gunicorn production server (default: Django dev server)
- `GUNICORN_WORKERS=4` - Number of Gunicorn worker processes
- `GUNICORN_THREADS=2` - Number of threads per worker
- `GUNICORN_TIMEOUT=120` - Request timeout in seconds

### Django App Structure

**Apps:**
- **core**: User authentication, events, and audit logging
- **crm**: Accounts, contacts, leads, opportunities, campaigns, tickets, and SLAs
- **erp**: Warehouses, products, inventory, invoices, payments, payroll, and HR
- **construction**: Projects, transactions, equipment, safety inspections, and documents

**API Endpoints (all under /api/v1/):**
- Users, Events, Audit Logs (core)
- Accounts, Contacts, Addresses, Leads, Opportunities, Campaigns, Tickets (crm)
- Warehouses, Products, Stock, Invoices, Payments, Employees, Payroll (erp)
- Projects, Equipment, Transactions, Safety Inspections, Documents (construction)

## CRM-ERP Data Flow Architecture

### The Account Entity: Central Bridge

The **Account** model in the CRM app serves as the master entity bridging CRM and ERP functionality. It is the single source of truth for customer/vendor data.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCOUNT (Master Entity)                       │
│  CRM Fields: name, industry, type, status, owner                │
│  ERP Fields: account_number, tax_id, payment_terms, credit_limit│
│  Sync Fields: last_synced_at, external_id                       │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    ┌─────────┐         ┌──────────┐         ┌──────────┐
    │ Contact │         │  Invoice │         │  Ticket  │
    │  (CRM)  │         │   (ERP)  │         │  (CRM)   │
    └─────────┘         └──────────┘         └──────────┘
         │                    │
         ▼                    ▼
    ┌─────────┐         ┌──────────┐
    │ Address │         │ Payment  │
    │  (CRM)  │         │   (ERP)  │
    └─────────┘         └──────────┘
```

### Data Flow Patterns

#### 1. Lead Conversion Flow (CRM → ERP)
```
Lead (CRM) → Contact + Account (CRM) → Customer Master (ERP)
                                    ↓
                              Invoice/Payment
```

#### 2. Order Processing Flow (CRM ↔ ERP)
```
Opportunity (CRM) → Sales Order (ERP) → Invoice (ERP) → Payment (ERP)
                                      ↓
                              General Ledger Entry
```

#### 3. Support Flow (CRM ← ERP)
```
Ticket (CRM) ← Account ← Invoice History (ERP)
     ↓                          ↓
SLA Tracking            Payment Status
```

### Domain Events for Sync

The system uses Django signals to emit domain events for cross-service synchronization:

**Account Events:**
- `account.created` - When a new account is created
- `account.updated` - When account details are modified
- `account.deleted` - When an account is removed

**Contact Events:**
- `contact.created` - When a new contact is added
- `contact.updated` - When contact details change
- `contact.deleted` - When a contact is removed

Events are stored in the `events` table with:
- Event type and payload (JSON)
- Processing status (pending/processed/failed)
- Retry count for failed events
- Source service identifier

### Account Schema (Enhanced)

The Account model includes fields for both CRM and ERP integration:

**CRM Fields:**
- `name`, `legal_name` - Company identification
- `industry`, `type`, `tier` - Classification
- `website`, `phone`, `email` - Contact info
- `owner`, `account_manager` - Assignment

**ERP Integration Fields:**
- `account_number` - Unique business identifier
- `tax_id`, `vat_number` - Tax compliance
- `payment_terms` - Net 15/30/45/60
- `credit_limit` - Financial controls
- `currency` - Default currency

**Sync Tracking:**
- `last_synced_at` - Last sync timestamp
- `external_id` - External system reference

### Data Storage

**Database:**
- PostgreSQL via DATABASE_URL environment variable
- Django ORM for database operations
- Django migrations for schema management

**Schema Design:**
- **Users**: Authentication table with username/password and role-based access
- **Accounts**: Master customer/vendor entity with CRM and ERP fields
- **Contacts**: Individuals linked to accounts with communication preferences
- **Projects**: Core entity tracking name, location, status, progress, budget, and due dates
- **Transactions**: Financial records linked to projects
- **Equipment**: Inventory management with warehouse and employee assignment
- **Safety Inspections**: Compliance tracking with findings and corrective actions
- **Documents**: File metadata with versioning

**Design Decisions:**
- **UUID Primary Keys**: Uses `uuid.uuid4()` for most tables
- **Decimal for Currency**: Uses `DecimalField` with appropriate precision
- **Timestamps**: Automatic `created_at` and `updated_at` fields
- **Foreign Keys**: Proper relationships between models with SET_NULL on delete
- **Domain Events**: Django signals emit events for cross-service sync

### Authentication & Authorization

The platform implements Role-Based Access Control (RBAC) using Microsoft Entra ID (Azure AD) for enterprise SSO authentication.

**User Roles:**
- `admin` / `Administrator` - Full access to all features
- `finance` / `Finance_User` - Access to invoices, payments, budgets, financial reports
- `hr` / `HR_Manager` - Access to employees, payroll, HR records
- `operations` / `Operations_Specialist` - Access to inventory, warehouses, equipment, orders
- `site_manager` / `Site_Manager` - Access to projects, safety, site-specific data
- `executive` / `Executive` - Read-only access to all data for oversight

**Azure AD Configuration:**

To enable Azure AD authentication, set the following environment variables:

Backend (Python/Django):
- `AZURE_AD_TENANT_ID` - Your Azure AD tenant ID
- `AZURE_AD_CLIENT_ID` - Your application's client ID

Frontend (React/Vite):
- `VITE_AZURE_AD_CLIENT_ID` - Same client ID as backend
- `VITE_AZURE_AD_TENANT_ID` - Same tenant ID as backend

**Azure AD App Registration Setup:**
1. Register an application in Microsoft Entra ID portal
2. Configure redirect URIs for your deployment URL
3. Define App Roles in the manifest (Finance_User, HR_Manager, Operations_Specialist, Site_Manager)
4. Assign users/groups to roles in Enterprise Applications

**Permission Classes (DRF):**
- `IsAuthenticated` - Requires valid Azure AD token
- `IsFinanceUser` - Requires Finance or Admin role
- `IsHRManager` - Requires HR or Admin role
- `IsOperationsSpecialist` - Requires Operations or Admin role
- `IsSiteManager` - Requires Site Manager or Admin role

**Auth Endpoint:**
- `GET /api/v1/auth/me/` - Returns current user profile, roles, and permissions

## Navigation and Interface Features

### Unified Global Search
- **Endpoint**: `/api/v1/search/?q={query}&limit={limit}`
- Searches across Contacts, Products, SalesOrders, and Tickets
- Results grouped by entity type with instant display
- Frontend component with keyboard shortcut (Cmd+K)

### Contextual Side Panel
- **Endpoint**: `/api/v1/accounts/{id}/related/`
- Shows related data when viewing an account:
  - Open tickets with status and priority
  - Recent invoices with amounts and due dates
  - Associated contacts with primary indicator
- Click any item to navigate to full record

### Smart Action Buttons
- Buttons that change based on record status
- Quote flow: "Edit Quote" → "Convert to Order" → "View Sales Order"
- Ticket flow: "Start Working" → "Resolve Ticket" → "Close Ticket"
- Configurable action mapping per entity type

### Favorites System
- **Endpoint**: `/api/v1/favorites/`
- Save frequently accessed records for quick access
- Toggle favorites via star icon in navigation
- Persists across sessions per user

### Entity Autocomplete
- **Account Lookup**: `/api/v1/accounts/lookup/?term={term}`
  - Returns billing address and payment terms
  - Used in order/invoice forms
- **Product Lookup**: `/api/v1/products/lookup/?term={term}`
  - Returns real-time stock availability
  - Shows in_stock/low_stock/out_of_stock status

### Breadcrumb Navigation
- Automatic breadcrumb generation from route
- Configurable labels per route segment
- Integration with favorites toggle

### External Dependencies

**Third-Party Services:**
- **PostgreSQL Database**: Database connection via DATABASE_URL
- **Replit Infrastructure**: Custom Vite plugins for Replit deployment

**Key Libraries (Python):**
- **Django**: Web framework
- **Django REST Framework**: API toolkit
- **django-cors-headers**: CORS handling
- **django-filter**: Queryset filtering
- **psycopg2-binary**: PostgreSQL adapter
- **whitenoise**: Static file serving

**Key Libraries (JavaScript/TypeScript):**
- **React Query**: Server state management with caching
- **http-proxy-middleware**: API proxying to Django
- **Radix UI**: Accessible component primitives
- **Tailwind CSS**: Utility-first styling
- **Zod**: Runtime type validation
- **React Hook Form**: Form state management
- **Lucide Icons**: Icon library

**Development Tools:**
- **TypeScript**: Type checking for frontend
- **Vite**: Fast development server with HMR
- **ESBuild**: Production bundling

**Build & Deployment:**
- Frontend builds to `dist/public` directory
- Django serves API at port 8000
- Express gateway at port 5000 proxies to Django
- Environment variable `DATABASE_URL` required for database connection
- Run `python manage.py migrate` to set up database schema
