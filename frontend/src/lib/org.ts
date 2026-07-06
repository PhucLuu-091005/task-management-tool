import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { Department, Team, User } from "@/lib/types";

// These list endpoints are admin-only; non-admins build choices from their own profile.
export function useUsers(enabled: boolean) {
  return useQuery<User[]>({
    queryKey: ["users"],
    queryFn: async () => (await api.get("/users/")).data,
    enabled,
  });
}

export function useTeams(enabled: boolean) {
  return useQuery<Team[]>({
    queryKey: ["teams"],
    queryFn: async () => (await api.get("/teams/")).data,
    enabled,
  });
}

export function useDepartments(enabled: boolean) {
  return useQuery<Department[]>({
    queryKey: ["departments"],
    queryFn: async () => (await api.get("/departments/")).data,
    enabled,
  });
}
