import { useState, useRef, useEffect } from 'react';
import { Link } from 'wouter';
import { Search, X, Users, Package, ShoppingCart, Ticket, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useGlobalSearch } from '@/hooks/use-global-search';
import type { SearchResult } from '@/lib/api';

const entityIcons = {
  contact: Users,
  product: Package,
  order: ShoppingCart,
  ticket: Ticket,
};

const entityColors = {
  contact: 'text-blue-400',
  product: 'text-emerald-400',
  order: 'text-amber-400',
  ticket: 'text-purple-400',
};

const entityLinks = {
  contact: (id: string) => `/dashboard/crm?contact=${id}`,
  product: (id: string) => `/dashboard/orders?product=${id}`,
  order: (id: string) => `/dashboard/orders?order=${id}`,
  ticket: (id: string) => `/dashboard/support?ticket=${id}`,
};

function SearchResultItem({ result, onClick }: { result: SearchResult; onClick: () => void }) {
  const Icon = entityIcons[result.type];
  const colorClass = entityColors[result.type];
  const link = entityLinks[result.type](result.id);

  return (
    <Link href={link} onClick={onClick}>
      <div 
        className="flex items-center gap-3 px-4 py-3 hover:bg-secondary cursor-pointer transition-colors"
        data-testid={`search-result-${result.type}-${result.id}`}
      >
        <div className={cn("p-2 rounded-sm bg-secondary", colorClass)}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{result.title}</div>
          <div className="text-xs text-muted-foreground truncate">{result.subtitle}</div>
        </div>
        <div className="text-xs text-muted-foreground capitalize">{result.type}</div>
      </div>
    </Link>
  );
}

function SearchResultGroup({ 
  title, 
  results, 
  type,
  onResultClick 
}: { 
  title: string; 
  results: SearchResult[]; 
  type: string;
  onResultClick: () => void;
}) {
  if (results.length === 0) return null;

  return (
    <div className="border-b border-border last:border-0">
      <div className="px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider bg-secondary/50">
        {title} ({results.length})
      </div>
      {results.map((result) => (
        <SearchResultItem key={`${type}-${result.id}`} result={result} onClick={onResultClick} />
      ))}
    </div>
  );
}

export function GlobalSearch() {
  const {
    query,
    results,
    isLoading,
    isOpen,
    handleSearch,
    clearSearch,
    closeResults,
    openResults,
    hasResults,
  } = useGlobalSearch();

  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        closeResults();
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [closeResults]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        inputRef.current?.focus();
        openResults();
      }
      if (event.key === 'Escape') {
        closeResults();
        inputRef.current?.blur();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [openResults, closeResults]);

  return (
    <div ref={containerRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="text"
          placeholder="Search contacts, products, orders..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={openResults}
          className="pl-10 pr-20 bg-secondary/50 border-border focus:border-primary/50 h-10"
          data-testid="global-search-input"
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          {query && (
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-6 w-6" 
              onClick={clearSearch}
              data-testid="clear-search-button"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
          <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-secondary px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>
      </div>

      {isOpen && query.length >= 2 && (
        <div 
          className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-sm shadow-xl max-h-[400px] overflow-auto z-50"
          data-testid="search-results-dropdown"
        >
          {isLoading && !hasResults && (
            <div className="p-8 text-center text-muted-foreground">
              <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
              <div className="text-sm">Searching...</div>
            </div>
          )}

          {!isLoading && !hasResults && query.length >= 2 && (
            <div className="p-8 text-center text-muted-foreground">
              <Search className="h-6 w-6 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No results found for "{query}"</div>
            </div>
          )}

          {results && hasResults && (
            <>
              <SearchResultGroup 
                title="Contacts" 
                results={results.contacts} 
                type="contact"
                onResultClick={closeResults} 
              />
              <SearchResultGroup 
                title="Products" 
                results={results.products} 
                type="product"
                onResultClick={closeResults} 
              />
              <SearchResultGroup 
                title="Orders" 
                results={results.orders} 
                type="order"
                onResultClick={closeResults} 
              />
              <SearchResultGroup 
                title="Tickets" 
                results={results.tickets} 
                type="ticket"
                onResultClick={closeResults} 
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
