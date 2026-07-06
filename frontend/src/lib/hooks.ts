import { useQuery } from "@tanstack/react-query";
import { isAxiosError } from "axios";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { User } from "@/lib/types";

export function useProfile() {
  const { authed } = useAuth();
  return useQuery<User>({
    queryKey: ["profile"],
    queryFn: async () => (await api.get("/users/profile/")).data,
    enabled: authed,
    retry: false,
  });
}

export function useRequireAuth(error?: unknown) {
  const router = useRouter();
  const { ready, authed } = useAuth();

  // Only an actual 401 means the session is gone; other errors (500, network)
  // are data failures the page renders in place, not a reason to sign out.
  const unauthorized = isAxiosError(error) && error.response?.status === 401;

  useEffect(() => {
    if (ready && (!authed || unauthorized)) router.replace("/login");
  }, [router, ready, authed, unauthorized]);
}
