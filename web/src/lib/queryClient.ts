import { QueryClient } from '@tanstack/react-query';
import { ApiError } from './api';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (count, error) => {
        if (error instanceof ApiError && [400, 401, 403, 404, 422].includes(error.status)) {
          return false;
        }
        return count < 2;
      },
      refetchOnWindowFocus: false,
    },
  },
});
