import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { Department, Team, User } from "@/lib/types";

// /teams/ and /departments/ stay admin-only, so non-admins build those choices
// from their own profile. /users/ is scoped server-side instead: admins get
// everyone, team/department leads get the members they're allowed to assign.
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
