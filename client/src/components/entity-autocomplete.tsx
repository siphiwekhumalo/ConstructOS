import { useState, useRef, useEffect } from 'react';
import { 
  Building2, 
  Package, 
  Loader2, 
  Check, 
  ChevronDown,
  AlertCircle
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useAccountLookup, useProductLookup } from '@/hooks/use-entity-lookup';
import type { AccountLookupResult, ProductLookupResult } from '@/lib/api';

interface AccountAutocompleteProps {
  value?: AccountLookupResult | null;
  onChange: (account: AccountLookupResult | null) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function AccountAutocomplete({ 
  value, 
  onChange, 
  placeholder = "Search accounts...",
  className,
  disabled = false,
}: AccountAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value?.name || '');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const { results, isLoading, search, clear } = useAccountLookup();

  useEffect(() => {
    if (value) {
      setInputValue(value.name);
    }
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    search(newValue);
    setIsOpen(true);
    if (!newValue) {
      onChange(null);
    }
  };

  const handleSelect = (account: AccountLookupResult) => {
    onChange(account);
    setInputValue(account.name);
    setIsOpen(false);
    clear();
  };

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="relative">
        <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => inputValue.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          className="pl-10 pr-10"
          disabled={disabled}
          data-testid="account-autocomplete-input"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          {value && !isLoading && <Check className="h-4 w-4 text-emerald-500" />}
        </div>
      </div>

      {isOpen && inputValue.length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-white/10 rounded-sm shadow-xl max-h-[300px] overflow-auto z-50">
          {isLoading && results.length === 0 && (
            <div className="p-4 text-center text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin mx-auto mb-1" />
              <div className="text-sm">Searching...</div>
            </div>
          )}

          {!isLoading && results.length === 0 && (
            <div className="p-4 text-center text-muted-foreground">
              <AlertCircle className="h-5 w-5 mx-auto mb-1" />
              <div className="text-sm">No accounts found</div>
            </div>
          )}

          {results.map((account) => (
            <div
              key={account.id}
              onClick={() => handleSelect(account)}
              className="p-3 hover:bg-white/5 cursor-pointer transition-colors border-b border-white/5 last:border-0"
              data-testid={`account-option-${account.id}`}
            >
              <div className="flex items-center justify-between gap-2">
                <div>
                  <div className="font-medium text-sm">{account.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {account.account_number} • {account.type}
                  </div>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {account.payment_terms.replace('_', ' ')}
                </Badge>
              </div>
              {account.billing_address && (
                <div className="text-xs text-muted-foreground mt-1">
                  {[account.billing_address.city, account.billing_address.state].filter(Boolean).join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface ProductAutocompleteProps {
  value?: ProductLookupResult | null;
  onChange: (product: ProductLookupResult | null) => void;
  warehouseId?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function ProductAutocomplete({ 
  value, 
  onChange, 
  warehouseId,
  placeholder = "Search products...",
  className,
  disabled = false,
}: ProductAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value?.name || '');
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { results, isLoading, search, clear } = useProductLookup(300, warehouseId);

  useEffect(() => {
    if (value) {
      setInputValue(value.name);
    }
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    search(newValue);
    setIsOpen(true);
    if (!newValue) {
      onChange(null);
    }
  };

  const handleSelect = (product: ProductLookupResult) => {
    onChange(product);
    setInputValue(product.name);
    setIsOpen(false);
    clear();
  };

  const stockStatusColors = {
    in_stock: 'bg-emerald-500/20 text-emerald-400',
    low_stock: 'bg-amber-500/20 text-amber-400',
    out_of_stock: 'bg-red-500/20 text-red-400',
  };

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="relative">
        <Package className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => inputValue.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          className="pl-10 pr-10"
          disabled={disabled}
          data-testid="product-autocomplete-input"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          {value && !isLoading && <Check className="h-4 w-4 text-emerald-500" />}
        </div>
      </div>

      {isOpen && inputValue.length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-white/10 rounded-sm shadow-xl max-h-[300px] overflow-auto z-50">
          {isLoading && results.length === 0 && (
            <div className="p-4 text-center text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin mx-auto mb-1" />
              <div className="text-sm">Searching...</div>
            </div>
          )}

          {!isLoading && results.length === 0 && (
            <div className="p-4 text-center text-muted-foreground">
              <AlertCircle className="h-5 w-5 mx-auto mb-1" />
              <div className="text-sm">No products found</div>
            </div>
          )}

          {results.map((product) => (
            <div
              key={product.id}
              onClick={() => handleSelect(product)}
              className="p-3 hover:bg-white/5 cursor-pointer transition-colors border-b border-white/5 last:border-0"
              data-testid={`product-option-${product.id}`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-sm">{product.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {product.sku} • ${product.unit_price}/{product.unit}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge 
                    variant="secondary" 
                    className={cn("text-xs", stockStatusColors[product.stock.status])}
                  >
                    {product.stock.status === 'in_stock' && `${product.stock.quantity} in stock`}
                    {product.stock.status === 'low_stock' && `Low: ${product.stock.quantity}`}
                    {product.stock.status === 'out_of_stock' && 'Out of stock'}
                  </Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
