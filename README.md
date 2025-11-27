# ConstructOS - Construction Management Platform

ConstructOS is a comprehensive construction management system that provides a full-stack solution for managing construction projects, equipment, safety inspections, finances, documents, and client relationships. Built with modern technologies, it offers enterprise-grade features including Role-Based Access Control (RBAC) with Microsoft Entra ID (Azure AD) authentication.

## Features

### Core Modules

- **Project Management**: Track construction projects with status, progress, budgets, and due dates
- **Equipment Management**: Inventory tracking with warehouse and employee assignment
- **Safety Inspections**: Compliance tracking with findings and corrective actions
- **Document Management**: File metadata with versioning support
- **Financial Management**: Invoices, payments, budgets, and transaction tracking

### CRM Capabilities

- **Account Management**: Master customer/vendor entity with CRM and ERP integration
- **Contact Management**: Track individuals linked to accounts
- **Lead Management**: Lead tracking with conversion to contacts/accounts
- **Opportunity Pipeline**: Sales opportunity tracking
- **Campaign Management**: Marketing campaign tracking
- **Ticket System**: Customer support with SLA tracking

### ERP Capabilities

- **Warehouse Management**: Multi-warehouse inventory control
- **Product Catalog**: Product management with SKU, pricing, and stock levels
- **Invoice & Payments**: Complete billing workflow
- **Employee Management**: HR records and employee tracking
- **Payroll**: Payroll record management
- **Sales & Purchase Orders**: Order management workflow

### Advanced Features

- **Unified Global Search**: Search across contacts, products, orders, and tickets (Cmd+K)
- **Contextual Side Panels**: Related data display for accounts
- **Favorites System**: Quick access to frequently used records
- **Entity Autocomplete**: Smart lookups for accounts and products
- **Role-Based Access Control**: Microsoft Entra ID integration with role-based permissions

## Technology Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling and development server
- **Tailwind CSS v4** for styling
- **shadcn/ui** component library (Radix UI primitives)
- **TanStack Query** for server state management
- **Wouter** for client-side routing
- **MSAL React** for Azure AD authentication

### Backend
- **Python 3.11+** with Django 5.2
- **Django REST Framework** for API development
- **Gunicorn** for production WSGI server
- **Express.js** as API gateway/proxy

### Database
- **PostgreSQL** (any PostgreSQL 13+ compatible database)

## Prerequisites

Before running locally, ensure you have the following installed:

- **Node.js** 20.x or higher
- **Python** 3.11 or higher
- **PostgreSQL** 13 or higher
- **npm** or **yarn** package manager
- **pip** or **uv** for Python package management

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd constructos
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration (Required)
DATABASE_URL=postgresql://username:password@localhost:5432/constructos

# Individual PostgreSQL variables (alternative to DATABASE_URL)
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=constructos

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Azure AD Configuration (Optional - for SSO)
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id

# Frontend Azure AD (Optional - for SSO)
VITE_AZURE_AD_CLIENT_ID=your-client-id
VITE_AZURE_AD_TENANT_ID=your-tenant-id

# Production Server (Optional)
USE_GUNICORN=false
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
```

### 3. Install Dependencies

#### Python Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip with pyproject.toml:
```bash
pip install .
```

Or install packages directly:
```bash
pip install django>=5.2 djangorestframework>=3.16.1 django-cors-headers>=4.9.0 \
    django-filter>=25.2 psycopg2-binary>=2.9.11 python-dotenv>=1.2.1 \
    whitenoise>=6.11.0 gunicorn>=23.0.0 msal>=1.34.0 "pyjwt[crypto]>=2.10.1" \
    cryptography>=46.0.3 faker>=38.2.0
```

#### Node.js Dependencies

```bash
npm install
```

### 4. Set Up the Database

Create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE constructos;

# Create user (optional)
CREATE USER constructos_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE constructos TO constructos_user;

# Exit
\q
```

Run Django migrations:

```bash
python manage.py migrate
```

Optionally seed with sample data:

```bash
python manage.py seed_data
```

### 5. Running the Application

#### Development Mode (Recommended)

Start both frontend and backend with a single command:

```bash
npm run dev
```

This will:
- Start the Express.js gateway on port 5000
- Start the Django backend on port 8000
- Start Vite dev server for hot module replacement
- Proxy API requests from `/api/v1/*` to Django

Access the application at: `http://localhost:5000`

#### Running Services Separately

**Terminal 1 - Django Backend:**
```bash
python manage.py runserver 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev:client
```

#### Production Mode

Build the frontend:
```bash
npm run build
```

Start the production server:
```bash
npm run start
```

Or with Gunicorn:
```bash
USE_GUNICORN=true npm run dev
```

## Project Structure

```
constructos/
├── backend/                    # Django backend
│   ├── apps/
│   │   ├── core/              # Users, authentication, events, favorites
│   │   ├── crm/               # CRM: accounts, contacts, leads, opportunities
│   │   ├── erp/               # ERP: products, inventory, invoices, payroll
│   │   └── construction/      # Projects, equipment, safety, documents
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI application
├── client/                     # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utilities and API client
│   │   └── pages/             # Page components
│   └── index.html             # HTML entry point
├── server/                     # Express.js gateway
│   ├── index-dev.ts           # Development server
│   └── index-prod.ts          # Production server
├── shared/                     # Shared TypeScript types
│   └── schema.ts              # Data models and schemas
├── manage.py                   # Django management script
├── package.json               # Node.js dependencies
├── pyproject.toml             # Python dependencies
└── vite.config.ts             # Vite configuration
```

## API Endpoints

All API endpoints are prefixed with `/api/v1/`:

### Authentication
- `GET /api/v1/auth/me/` - Current user profile, roles, and permissions

### Core
- `GET/POST /api/v1/users/` - User management
- `GET/POST /api/v1/events/` - Event management
- `GET/POST /api/v1/favorites/` - User favorites
- `GET /api/v1/search/` - Global search

### CRM
- `GET/POST /api/v1/accounts/` - Account management
- `GET /api/v1/accounts/{id}/related/` - Account related data
- `GET /api/v1/accounts/lookup/` - Account autocomplete
- `GET/POST /api/v1/contacts/` - Contact management
- `GET/POST /api/v1/leads/` - Lead management
- `POST /api/v1/leads/{id}/convert/` - Convert lead to contact/account
- `GET/POST /api/v1/opportunities/` - Opportunity management
- `GET/POST /api/v1/campaigns/` - Campaign management
- `GET/POST /api/v1/tickets/` - Ticket management

### ERP
- `GET/POST /api/v1/warehouses/` - Warehouse management
- `GET/POST /api/v1/products/` - Product management
- `GET /api/v1/products/lookup/` - Product autocomplete with stock
- `GET/POST /api/v1/stock/` - Stock management
- `GET/POST /api/v1/invoices/` - Invoice management
- `GET/POST /api/v1/payments/` - Payment management
- `GET/POST /api/v1/employees/` - Employee management
- `GET/POST /api/v1/payroll/` - Payroll records
- `GET/POST /api/v1/sales-orders/` - Sales orders
- `GET/POST /api/v1/purchase-orders/` - Purchase orders

### Construction
- `GET/POST /api/v1/projects/` - Project management
- `GET/POST /api/v1/equipment/` - Equipment management
- `GET/POST /api/v1/transactions/` - Financial transactions
- `GET/POST /api/v1/safety/inspections/` - Safety inspections
- `GET/POST /api/v1/documents/` - Document management

### Analytics
- `GET /api/v1/analytics/dashboard/` - Dashboard statistics

## Azure AD Configuration (Optional)

To enable Microsoft Entra ID (Azure AD) authentication:

### 1. Register an Application

1. Go to the [Microsoft Entra admin center](https://entra.microsoft.com/)
2. Navigate to **Identity > Applications > App registrations**
3. Click **New registration**
4. Enter a name for your application
5. Set the redirect URI to your application URL (e.g., `http://localhost:5000`)
6. Click **Register**

### 2. Configure the Application

1. Note the **Application (client) ID** and **Directory (tenant) ID**
2. Under **Authentication**, add platform configurations:
   - Single-page application: `http://localhost:5000`
3. Under **API permissions**, add:
   - Microsoft Graph: `User.Read`
4. Under **App roles**, create roles:
   - `Finance_User` - Access to financial features
   - `HR_Manager` - Access to HR features
   - `Operations_Specialist` - Access to operations features
   - `Site_Manager` - Access to site management features
   - `Administrator` - Full access

### 3. Assign Users to Roles

1. Go to **Enterprise Applications**
2. Find your application
3. Under **Users and groups**, assign users to the appropriate roles

### 4. Update Environment Variables

```bash
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id
VITE_AZURE_AD_CLIENT_ID=your-client-id
VITE_AZURE_AD_TENANT_ID=your-tenant-id
```

## User Roles and Permissions

| Role | Access |
|------|--------|
| Administrator | Full access to all features |
| Finance_User | Invoices, payments, budgets, financial reports |
| HR_Manager | Employees, payroll, HR records |
| Operations_Specialist | Inventory, warehouses, equipment, orders |
| Site_Manager | Projects, safety, site-specific data |
| Executive | Read-only access to all data |

## Development

### Running Tests

```bash
# Django tests
python manage.py test

# TypeScript type checking
npm run check
```

### Database Migrations

Create new migrations after model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding New Features

1. Define models in the appropriate Django app
2. Create serializers for API representation
3. Add ViewSets and register routes
4. Update TypeScript types in `shared/schema.ts`
5. Create React components and hooks
6. Add API client functions in `client/src/lib/api.ts`

## Docker Setup (Alternative)

You can also run the application using Docker:

### docker-compose.yml

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: constructos
      POSTGRES_USER: constructos
      POSTGRES_PASSWORD: constructos_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://constructos:constructos_password@db:5432/constructos
      DJANGO_SECRET_KEY: your-secret-key
      DJANGO_DEBUG: "True"
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    environment:
      VITE_AZURE_AD_CLIENT_ID: ${VITE_AZURE_AD_CLIENT_ID:-}
      VITE_AZURE_AD_TENANT_ID: ${VITE_AZURE_AD_TENANT_ID:-}
    ports:
      - "5000:5000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Dockerfile.backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install .

COPY backend/ ./backend/
COPY manage.py .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "backend.wsgi:application"]
```

### Dockerfile.frontend

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5000

CMD ["npm", "run", "dev"]
```

### Running with Docker

```bash
# Build and start all services
docker-compose up --build

# Run migrations
docker-compose exec backend python manage.py migrate

# Seed data (optional)
docker-compose exec backend python manage.py seed_data
```

## Troubleshooting

### Port Already in Use

If port 8000 or 5000 is already in use:

```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

### Database Connection Issues

Verify PostgreSQL is running:
```bash
pg_isready -h localhost -p 5432
```

Check connection string format:
```
postgresql://user:password@host:port/database
```

### Missing Dependencies

Reinstall all dependencies:
```bash
rm -rf node_modules
npm install

pip install --upgrade -r requirements.txt
```

### Migration Issues

Reset migrations if needed:
```bash
python manage.py migrate --fake-initial
```

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the repository.
