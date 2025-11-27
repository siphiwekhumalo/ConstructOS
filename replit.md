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
- `chat`: Real-time team messaging with WebSocket support.

### Data Storage

**Database:** PostgreSQL (configured via `DATABASE_URL`).

**Schema Design:**
- UUID Primary Keys for most tables.
- DecimalField for currency.
- Automatic `created_at` and `updated_at` timestamps.
- Foreign key relationships with `SET_NULL` on delete.
- Domain events using Django signals for cross-service sync.

### Authentication & Authorization

Role-Based Access Control (RBAC) using Microsoft Entra ID (Azure AD) for SSO and credential-based authentication.

**User Roles (11 total):** `system_admin`, `executive`, `finance_manager`, `hr_specialist`, `sales_rep`, `operations_specialist`, `site_manager`, `warehouse_clerk`, `field_worker`, `subcontractor`, `client`.

**Configuration:** Requires Azure AD Tenant ID and Client ID for both backend and frontend. App roles defined in Azure AD manifest for permission mapping.

### Enterprise Security Features

**Token Blacklisting:**
- Redis-based JWT token blacklist for secure logout
- Session token invalidation on logout
- Force logout capability for administrators (`/api/v1/security/force-logout/`)
- Token version tracking for bulk invalidation

**Brute Force Protection:**
- Account lockout after 5 failed login attempts
- 15-minute lockout window
- Failed attempt tracking with Redis
- Automatic unlock after lockout period

**Rate Limiting:**
- Per-IP rate limiting on authentication endpoints (10 requests/minute)
- Configurable limits per endpoint
- Rate limit headers in responses (X-RateLimit-Remaining)

**Security Logging & Monitoring:**
- Centralized security event logging via Redis
- Event types: LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, TOKEN_BLACKLISTED, PERMISSION_DENIED, RATE_LIMIT_EXCEEDED, BRUTE_FORCE_DETECTED, ANOMALY_DETECTED, DATA_MODIFIED, DATA_DELETED, SENSITIVE_ACCESS, AFTER_HOURS_ACCESS
- Security dashboard API (`/api/v1/security/dashboard/`) for administrators
- Security events API (`/api/v1/security/events/`) with filtering

**Input Validation & XSS Prevention:**
- Security middleware for XSS pattern detection
- SQL injection pattern detection
- HTML entity encoding for dangerous characters
- Request body sanitization
- Query parameter validation

**Anomaly Detection:**
- After-hours access detection (outside 6 AM - 10 PM)
- API call volume spike detection
- User behavior tracking for pattern analysis

**Security Headers:**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security (on HTTPS)

### Navigation and Interface Features

- **Unified Global Search**: Searches across key entities (`/api/v1/search/`).
- **Contextual Side Panel**: Displays related data for specific records (e.g., related tickets/invoices for an account).
- **Smart Action Buttons**: Dynamically change based on record status.
- **Favorites System**: Allows users to save frequently accessed records.
- **Entity Autocomplete**: Provides real-time lookups (e.g., account details, product stock).
- **Breadcrumb Navigation**: Automatic generation from route.

### Global Scalability Features

**Caching & Performance:**
- **Redis Caching**: Distributed cache for sessions, user roles, and frequently accessed data with django-redis.
- **Celery Task Queue**: Async task processing with Redis broker for report generation, notifications, and data sync.
- **Cache Decorators**: `@cached()` decorator for API views with configurable TTL.

**Document Management:**
- **Azure Blob Storage**: Enterprise document storage with SAS token authentication.
- **Document Upload API**: `/api/v1/documents/upload/` for multipart file uploads.
- **Secure Downloads**: Time-limited SAS URLs for document access.

**Observability:**
- **OpenTelemetry**: Distributed tracing with OTLP export for cross-service monitoring.
- **Traced Decorators**: `@traced()` decorator for automatic span creation.
- **Health Checks**: Kubernetes readiness (`/api/v1/health/readiness/`) and liveness (`/api/v1/health/liveness/`) probes.

**Internationalization:**
- **i18next**: Multi-language support with English, Afrikaans (af), and isiZulu (zu).
- **Language Detection**: Auto-detect from browser or localStorage.
- **Translation Files**: `/public/locales/{lang}/translation.json`.

### Real-Time Chat (Team Messaging)

**Architecture:**
- **Dual Server Setup**: Gunicorn (port 8000) for REST API, Daphne (port 8001) for ASGI/WebSocket connections.
- **Channel Layer**: Redis-backed Django Channels for message distribution across workers.
- **WebSocket Proxy**: Express gateway proxies `/ws` path to Daphne server with upgrade support.

**Features:**
- **Chat Rooms**: Public, private, direct, and project-linked channels.
- **Real-time Messaging**: WebSocket-based instant message delivery with typing indicators.
- **Presence Tracking**: Online/offline status for team members.
- **Message Reactions**: Emoji reactions on messages.
- **Thread Replies**: Reply-to functionality for message threads.
- **Unread Counts**: Per-room unread message tracking.

**Data Models:**
- `ChatRoom`: Room metadata with room_type (public/private/direct/project).
- `Message`: Text messages with sender, mentions, attachments, and parent references.
- `RoomMembership`: User membership with roles (admin/moderator/member).
- `MessageReaction`: Emoji reactions with user attribution.
- `TypingIndicator`: Transient typing status for real-time feedback.

**API Endpoints:**
- `GET/POST /api/v1/chat/rooms/`: List and create chat rooms.
- `GET /api/v1/chat/rooms/{id}/messages/`: Retrieve room messages with pagination.
- `POST /api/v1/chat/rooms/{id}/join/`: Join a room.
- `POST /api/v1/chat/rooms/{id}/leave/`: Leave a room.
- `WebSocket /ws/chat/{room_id}/`: Real-time message stream.

## External Dependencies

**Third-Party Services:**
- **PostgreSQL Database**
- **Microsoft Entra ID (Azure AD)** for authentication.
- **Redis** for caching and Celery message broker.
- **Azure Blob Storage** for document management.

**Key Libraries (Python):**
- Django, Django REST Framework, django-cors-headers, django-filter, psycopg2-binary, whitenoise.
- django-redis, celery for caching and async tasks.
- azure-storage-blob for document storage.
- opentelemetry-sdk, opentelemetry-instrumentation-django for tracing.
- channels, channels-redis, daphne for WebSocket support.

**Key Libraries (JavaScript/TypeScript):**
- React Query, http-proxy-middleware, Radix UI, Tailwind CSS, Zod, React Hook Form, Lucide Icons.
- i18next, react-i18next, i18next-browser-languagedetector for internationalization.

**Development Tools:**
- TypeScript, Vite, ESBuild.
- pytest, pytest-django, pytest-cov for testing.

**Build & Deployment:**
- Utilizes Azure Pipelines for CI/CD to Azure Kubernetes Service (AKS).
- Docker for containerization, with multi-stage builds.
- Kubernetes manifests for deployment, scaling, and configuration.
- Nginx ingress with TLS termination.

## Environment Variables

**Required for Production:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379/0)
- `AZURE_STORAGE_CONNECTION_STRING` or `AZURE_STORAGE_ACCOUNT` + `AZURE_STORAGE_KEY`: Azure Blob Storage credentials
- `AZURE_STORAGE_CONTAINER`: Document container name (default: constructos-documents)
- `OTEL_ENABLED`: Enable OpenTelemetry tracing (true/false)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP collector endpoint

## Recent Changes (November 2025)

- Added Redis distributed caching layer with django-redis
- Implemented Celery for async task processing
- Added Azure Blob Storage integration for document management
- Integrated OpenTelemetry for distributed tracing
- Added internationalization with i18next (en, af, zu languages)
- Created Kubernetes health check endpoints for liveness/readiness probes
- Enhanced testing framework with 256+ pytest tests and authenticated API clients
- Implemented real-time team chat with Django Channels WebSocket support
- Added dual-server architecture (Gunicorn + Daphne) for WSGI/ASGI separation
- Created React chat UI with ChatRoomList and ChatMessagePane components