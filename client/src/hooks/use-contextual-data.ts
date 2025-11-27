import { useQuery } from '@tanstack/react-query';
import { getAccountRelated, type AccountRelatedData } from '@/lib/api';

export function useAccountRelatedData(accountId: string | null) {
  return useQuery<AccountRelatedData>({
    queryKey: ['account-related', accountId],
    queryFn: () => getAccountRelated(accountId!),
    enabled: !!accountId,
    staleTime: 60000,
  });
}

export function useContextualData(entityType: string, entityId: string | null) {
  const accountQuery = useAccountRelatedData(
    entityType === 'account' ? entityId : null
  );

  if (entityType === 'account') {
    return {
      data: accountQuery.data,
      isLoading: accountQuery.isLoading,
      error: accountQuery.error,
    };
  }

  return {
    data: null,
    isLoading: false,
    error: null,
  };
}
