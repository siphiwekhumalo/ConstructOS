# ConstructOS - Construction Management Platform

## Overview

ConstructOS is a comprehensive construction management system built with Python, Django, TypeScript, and React. The application provides a full-stack solution for managing construction projects, equipment, safety inspections, finances, documents, and client relationships. It leverages modern web technologies including shadcn/ui components, Tailwind CSS, and a PostgreSQL database via Drizzle ORM.

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
- Node.js with Express.js framework
- TypeScript for type safety across the stack
- Drizzle ORM for database operations
- Separate development and production server configurations

**Design Decisions:**
- **API Structure**: RESTful API design with routes organized in `/api` namespace. All routes defined in `server/routes.ts`.
- **Request Logging**: Custom middleware logs API requests with timing, method, path, status code, and response data (truncated for readability).
- **Development vs Production**: Separate entry points (`index-dev.ts` and `index-prod.ts`) allow for different behavior. Development mode integrates Vite middleware for HMR, while production serves static files.
- **Database Seeding**: Automatic seeding in development environment to provide sample data for testing.

### Data Storage

**Database:**
- PostgreSQL via Neon serverless
- Drizzle ORM for type-safe database queries and migrations
- WebSocket support for serverless database connections

**Schema Design:**
- **Users**: Authentication table with username/password
- **Projects**: Core entity tracking project name, location, status, progress, budget, and due dates
- **Transactions**: Financial records linked to projects
- **Equipment**: Inventory management for tools and materials
- **Safety Inspections**: Compliance tracking with inspection records
- **Clients**: CRM data for customer management
- **Documents**: File metadata and references

**Design Decisions:**
- **UUID Primary Keys**: Uses `gen_random_uuid()` for most tables to avoid sequential ID enumeration attacks
- **Text Fields for Dates**: Due dates stored as text for flexibility (may need revision for date queries)
- **Decimal for Currency**: Uses `decimal(12, 2)` for precise financial calculations
- **Timestamps**: Automatic `createdAt` timestamps for audit trails
- **Foreign Keys**: Projects referenced by transactions for data integrity

### Authentication & Authorization

Currently implements basic user schema with username/password fields. No session management or JWT implementation visible in the codebase yet. The `connect-pg-simple` dependency suggests intent for PostgreSQL-backed session storage.

**Future Consideration**: Authentication appears to be planned but not fully implemented.

### External Dependencies

**Third-Party Services:**
- **Neon Database**: Serverless PostgreSQL hosting with WebSocket support for edge environments
- **Replit Infrastructure**: Custom Vite plugins for Replit deployment (`@replit/vite-plugin-cartographer`, `@replit/vite-plugin-dev-banner`, `@replit/vite-plugin-runtime-error-modal`)

**Key Libraries:**
- **React Query**: Server state management with caching
- **Drizzle ORM**: Type-safe database queries and schema management
- **Radix UI**: Accessible component primitives (30+ component packages)
- **Tailwind CSS**: Utility-first styling
- **Zod**: Runtime type validation for API inputs
- **React Hook Form**: Form state management with validation
- **Lucide Icons**: Icon library for UI elements
- **date-fns**: Date manipulation utilities

**Development Tools:**
- **TypeScript**: Type checking across frontend and backend
- **Vite**: Fast development server with HMR
- **ESBuild**: Production bundling for server code
- **Drizzle Kit**: Database migration management

**Build & Deployment:**
- Frontend builds to `dist/public` directory
- Backend bundles to `dist/index.js` using ESBuild
- Environment variable `DATABASE_URL` required for database connection
- Supports Replit deployment with custom meta image plugins