import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getFavorites, addFavorite, removeFavorite, type Favorite } from '@/lib/api';

export function useFavorites(userId?: string) {
  const queryClient = useQueryClient();

  const { data: favorites = [], isLoading, error } = useQuery<Favorite[]>({
    queryKey: ['favorites', userId],
    queryFn: () => getFavorites(userId),
    staleTime: 60000,
  });

  const addMutation = useMutation({
    mutationFn: addFavorite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  const removeMutation = useMutation({
    mutationFn: removeFavorite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  const isFavorite = (entityType: string, entityId: string) => {
    return favorites.some(
      (f) => f.entity_type === entityType && f.entity_id === entityId
    );
  };

  const toggleFavorite = (
    userId: string,
    entityType: string,
    entityId: string,
    entityTitle: string,
    entitySubtitle?: string
  ) => {
    const existing = favorites.find(
      (f) => f.entity_type === entityType && f.entity_id === entityId
    );

    if (existing) {
      removeMutation.mutate(existing.id);
    } else {
      addMutation.mutate({
        user: userId,
        entity_type: entityType,
        entity_id: entityId,
        entity_title: entityTitle,
        entity_subtitle: entitySubtitle || null,
      });
    }
  };

  return {
    favorites,
    isLoading,
    error,
    isFavorite,
    toggleFavorite,
    addFavorite: addMutation.mutate,
    removeFavorite: removeMutation.mutate,
    isAdding: addMutation.isPending,
    isRemoving: removeMutation.isPending,
  };
}
