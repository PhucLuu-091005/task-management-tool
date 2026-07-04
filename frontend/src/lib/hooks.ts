import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { api } from "@/lib/api";
import { hasSession } from "@/lib/auth-storage";
import { User } from "@/lib/types";

export function useProfile() {
  return useQuery<User>({
    queryKey: ["profile"],
    queryFn: async () => (await api.get("/users/profile/")).data,
    retry: false,
  });
}

export function useRequireAuth(isError = false) {
  const router = useRouter();

  useEffect(() => {
    // isError covers the case where the refresh flow failed and tokens were cleared.
    if (!hasSession() || isError) router.replace("/login");
  }, [router, isError]);
}
