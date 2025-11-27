# ConstructOS - Construction Management Platform

## Overview

ConstructOS is a comprehensive construction management system built with Python, Django, TypeScript, and React. It provides a full-stack solution for managing construction projects, equipment, safety inspections, finances, documents, and client relationships. The platform aims to modernize construction workflows with features spanning project planning, equipment tracking, safety compliance, IoT monitoring, CRM capabilities, and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:** React 18+ (TypeScript), Vite, Wouter, TanStack Query, shadcn/ui, Tailwind CSS v4.

**Design Decisions:**
- **Component Library**: shadcn/ui (New York variant) for consistent, accessible UI.
- **State Management**: TanStack Query for server state (aggressive caching), React hooks for client state.
- **Routing**: Lightweight Wouter for client-side navigation.
- **Styling**: Tailwind CSS with CSS variables for theming and custom typography.

### Backend Architecture

**Technology Stack:** Python 3.11, Django 5.2, Django REST Framework, Gunicorn, Express.js (as API gateway/proxy).

**Design Decisions:**
- **API Structure**: RESTful API with versioned `/api/v1` endpoints.
- **Proxy Architecture**: Express proxies API requests to Django and serves the React frontend.
- **Production Server**: Gunicorn serves Django in production for concurrency.
- **Development Setup**: Express spawns Django (dev server or Gunicorn) for unified development.
- **CRM-ERP Data Flow**: The Account model is the central entity bridging CRM and ERP functionalities, facilitating lead conversion, order processing, and support flows. Domain events (Django signals) are used for cross-service synchronization.

### Django App Structure

**Core Apps:**
- `core`: User authentication, events, audit logging.
- `crm`: Accounts, contacts, leads, opportunities, campaigns, tickets.
- `erp`: Warehouses, products, inventory, invoices, payments, payroll, HR.
- `construction`: Projects, transactions, equipment, safety inspections, documents.

### Data Storage

**Database:** PostgreSQL (configured via `DATABASE_URL`).

**Schema Design:**
- UUID Primary Keys for most tables.
- DecimalField for currency.
- Automatic `created_at` and `updated_at` timestamps.
- Foreign key relationships with `SET_NULL` on delete.
- Domain events using Django signals for cross-service sync.

### Authentication & Authorization

Role-Based Access Control (RBAC) using Microsoft Entra ID (Azure AD) for SSO.

**User Roles:** `admin`, `finance`, `hr`, `operations`, `site_manager`, `executive`.

**Configuration:** Requires Azure AD Tenant ID and Client ID for both backend and frontend. App roles defined in Azure AD manifest for permission mapping.

### Navigation and Interface Features

- **Unified Global Search**: Searches across key entities (`/api/v1/search/`).
- **Contextual Side Panel**: Displays related data for specific records (e.g., related tickets/invoices for an account).
- **Smart Action Buttons**: Dynamically change based on record status.
- **Favorites System**: Allows users to save frequently accessed records.
- **Entity Autocomplete**: Provides real-time lookups (e.g., account details, product stock).
- **Breadcrumb Navigation**: Automatic generation from route.

## External Dependencies

**Third-Party Services:**
- **PostgreSQL Database**
- **Microsoft Entra ID (Azure AD)** for authentication.

**Key Libraries (Python):**
- Django, Django REST Framework, django-cors-headers, django-filter, psycopg2-binary, whitenoise.

**Key Libraries (JavaScript/TypeScript):**
- React Query, http-proxy-middleware, Radix UI, Tailwind CSS, Zod, React Hook Form, Lucide Icons.

**Development Tools:**
- TypeScript, Vite, ESBuild.

**Build & Deployment:**
- Utilizes Azure Pipelines for CI/CD to Azure Kubernetes Service (AKS).
- Docker for containerization, with multi-stage builds.
- Kubernetes manifests for deployment, scaling, and configuration.