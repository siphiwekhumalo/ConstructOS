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
- Express.js as API gateway/proxy (port 5000)
- Django development server (port 8000)

**Design Decisions:**
- **API Structure**: RESTful API design with versioned `/api/v1` endpoints. Django handles all business logic and database operations.
- **Proxy Architecture**: Express serves as an API gateway, proxying `/api/v1/*` requests to Django while serving the React frontend via Vite.
- **Development Setup**: Express spawns Django as a child process for unified development workflow. Both servers start with a single `npm run dev` command.
- **Request Logging**: Custom middleware logs API requests with timing, method, path, and status codes.

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

### Data Storage

**Database:**
- PostgreSQL via DATABASE_URL environment variable
- Django ORM for database operations
- Django migrations for schema management

**Schema Design:**
- **Users**: Authentication table with username/password and role-based access
- **Projects**: Core entity tracking name, location, status, progress, budget, and due dates
- **Transactions**: Financial records linked to projects
- **Equipment**: Inventory management with warehouse and employee assignment
- **Safety Inspections**: Compliance tracking with findings and corrective actions
- **Clients**: CRM data linked to accounts
- **Documents**: File metadata with versioning

**Design Decisions:**
- **UUID Primary Keys**: Uses `uuid.uuid4()` for most tables
- **Decimal for Currency**: Uses `DecimalField` with appropriate precision
- **Timestamps**: Automatic `created_at` and `updated_at` fields
- **Foreign Keys**: Proper relationships between models with SET_NULL on delete

### Authentication & Authorization

Currently implements basic user schema with username/password fields. Django REST Framework provides token authentication capabilities.

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
