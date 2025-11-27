import { useState, useCallback, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { globalSearch, type SearchResults } from '@/lib/api';

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

export function useGlobalSearch(debounceMs = 300) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const debouncedSetQuery = useCallback(
    debounce((value: string) => {
      setDebouncedQuery(value);
    }, debounceMs),
    [debounceMs]
  );

  useEffect(() => {
    debouncedSetQuery(query);
  }, [query, debouncedSetQuery]);

  const { data, isLoading, error } = useQuery<SearchResults>({
    queryKey: ['global-search', debouncedQuery],
    queryFn: () => globalSearch(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 30000,
  });

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    if (value.length >= 2) {
      setIsOpen(true);
    }
  }, []);

  const clearSearch = useCallback(() => {
    setQuery('');
    setDebouncedQuery('');
    setIsOpen(false);
  }, []);

  const closeResults = useCallback(() => {
    setIsOpen(false);
  }, []);

  const openResults = useCallback(() => {
    if (query.length >= 2) {
      setIsOpen(true);
    }
  }, [query]);

  return {
    query,
    results: data,
    isLoading,
    error,
    isOpen,
    handleSearch,
    clearSearch,
    closeResults,
    openResults,
    hasResults: data && data.total > 0,
  };
}
