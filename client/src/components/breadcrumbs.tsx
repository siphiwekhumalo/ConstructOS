import { Link, useLocation } from 'wouter';
import { ChevronRight, Home, Star, StarOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useFavorites } from '@/hooks/use-favorites';

interface BreadcrumbItem {
  label: string;
  href: string;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  currentPage?: string;
  entityType?: string;
  entityId?: string;
  entityTitle?: string;
  showFavorite?: boolean;
  userId?: string;
  className?: string;
}

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  projects: 'Projects',
  documents: 'Documents',
  finance: 'Finance',
  equipment: 'Equipment',
  safety: 'Safety',
  iot: 'IoT Monitor',
  crm: 'CRM',
  orders: 'Orders',
  hr: 'Human Resources',
  support: 'Support',
  reports: 'Reports',
  settings: 'Settings',
};

function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];
  
  let currentPath = '';
  
  for (const segment of segments) {
    currentPath += `/${segment}`;
    const label = routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
    breadcrumbs.push({
      label,
      href: currentPath,
    });
  }
  
  return breadcrumbs;
}

export function Breadcrumbs({ 
  items,
  currentPage,
  entityType,
  entityId,
  entityTitle,
  showFavorite = false,
  userId,
  className 
}: BreadcrumbsProps) {
  const [location] = useLocation();
  const { isFavorite, toggleFavorite, isAdding, isRemoving } = useFavorites(userId);
  
  const breadcrumbItems = items || generateBreadcrumbs(location);
  const isFav = entityType && entityId ? isFavorite(entityType, entityId) : false;
  const isProcessing = isAdding || isRemoving;

  const handleToggleFavorite = () => {
    if (entityType && entityId && entityTitle && userId) {
      toggleFavorite(userId, entityType, entityId, entityTitle);
    }
  };

  return (
    <nav 
      className={cn("flex items-center gap-2 text-sm", className)}
      aria-label="Breadcrumb"
      data-testid="breadcrumbs"
    >
      <ol className="flex items-center gap-1">
        <li>
          <Link href="/dashboard">
            <span className="text-muted-foreground hover:text-foreground transition-colors cursor-pointer flex items-center">
              <Home className="h-4 w-4" />
            </span>
          </Link>
        </li>
        
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;
          
          return (
            <li key={item.href} className="flex items-center gap-1">
              <ChevronRight className="h-4 w-4 text-muted-foreground/50" />
              {isLast ? (
                <span className="font-medium text-foreground">
                  {currentPage || item.label}
                </span>
              ) : (
                <Link href={item.href}>
                  <span className="text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                    {item.label}
                  </span>
                </Link>
              )}
            </li>
          );
        })}
      </ol>

      {showFavorite && entityType && entityId && userId && (
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "h-7 w-7 ml-2",
            isFav && "text-amber-400 hover:text-amber-500"
          )}
          onClick={handleToggleFavorite}
          disabled={isProcessing}
          data-testid="toggle-favorite-button"
        >
          {isFav ? (
            <Star className="h-4 w-4 fill-current" />
          ) : (
            <StarOff className="h-4 w-4" />
          )}
        </Button>
      )}
    </nav>
  );
}

interface FavoritesListProps {
  userId: string;
  className?: string;
  maxItems?: number;
}

export function FavoritesList({ userId, className, maxItems = 5 }: FavoritesListProps) {
  const { favorites, isLoading } = useFavorites(userId);

  const entityIcons: Record<string, string> = {
    account: '🏢',
    contact: '👤',
    product: '📦',
    order: '🛒',
    ticket: '🎫',
    project: '📁',
  };

  const entityLinks: Record<string, (id: string) => string> = {
    account: (id) => `/dashboard/crm?account=${id}`,
    contact: (id) => `/dashboard/crm?contact=${id}`,
    product: (id) => `/dashboard/orders?product=${id}`,
    order: (id) => `/dashboard/orders?order=${id}`,
    ticket: (id) => `/dashboard/support?ticket=${id}`,
    project: (id) => `/dashboard/projects?project=${id}`,
  };

  if (isLoading || favorites.length === 0) {
    return null;
  }

  const displayFavorites = favorites.slice(0, maxItems);

  return (
    <div className={cn("space-y-1", className)}>
      <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-4 py-2">
        Favorites
      </div>
      {displayFavorites.map((favorite) => {
        const link = entityLinks[favorite.entity_type]?.(favorite.entity_id) || '/dashboard';
        const icon = entityIcons[favorite.entity_type] || '📄';
        
        return (
          <Link key={favorite.id} href={link}>
            <div 
              className="flex items-center gap-2 px-4 py-2 hover:bg-white/5 cursor-pointer transition-colors text-sm"
              data-testid={`favorite-${favorite.id}`}
            >
              <span>{icon}</span>
              <span className="truncate">{favorite.entity_title}</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
