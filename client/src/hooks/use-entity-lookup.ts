import { useState, useCallback, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  lookupAccounts, 
  lookupProducts, 
  type AccountLookupResult, 
  type ProductLookupResult 
} from '@/lib/api';

function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), wait);
  };
}

export function useAccountLookup(debounceMs = 300) {
  const [term, setTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');

  const debouncedSetTerm = useCallback(
    debounce((value: string) => {
      setDebouncedTerm(value);
    }, debounceMs),
    [debounceMs]
  );

  useEffect(() => {
    debouncedSetTerm(term);
  }, [term, debouncedSetTerm]);

  const { data, isLoading, error } = useQuery<AccountLookupResult[]>({
    queryKey: ['account-lookup', debouncedTerm],
    queryFn: () => lookupAccounts(debouncedTerm),
    enabled: debouncedTerm.length >= 2,
    staleTime: 30000,
  });

  const search = useCallback((value: string) => {
    setTerm(value);
  }, []);

  const clear = useCallback(() => {
    setTerm('');
    setDebouncedTerm('');
  }, []);

  return {
    term,
    results: data || [],
    isLoading,
    error,
    search,
    clear,
  };
}

export function useProductLookup(debounceMs = 300, warehouseId?: string) {
  const [term, setTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');

  const debouncedSetTerm = useCallback(
    debounce((value: string) => {
      setDebouncedTerm(value);
    }, debounceMs),
    [debounceMs]
  );

  useEffect(() => {
    debouncedSetTerm(term);
  }, [term, debouncedSetTerm]);

  const { data, isLoading, error } = useQuery<ProductLookupResult[]>({
    queryKey: ['product-lookup', debouncedTerm, warehouseId],
    queryFn: () => lookupProducts(debouncedTerm, 10, warehouseId),
    enabled: debouncedTerm.length >= 2,
    staleTime: 30000,
  });

  const search = useCallback((value: string) => {
    setTerm(value);
  }, []);

  const clear = useCallback(() => {
    setTerm('');
    setDebouncedTerm('');
  }, []);

  return {
    term,
    results: data || [],
    isLoading,
    error,
    search,
    clear,
  };
}
