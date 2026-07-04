import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { User } from "@/lib/types";

export function useProfile() {
  return useQuery<User>({
    queryKey: ["profile"],
    queryFn: async () => (await api.get("/users/profile/")).data,
    retry: false,
  });
}
