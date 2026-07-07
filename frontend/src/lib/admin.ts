import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import {
  Department,
  DepartmentPayload,
  Role,
  Team,
  TeamMemberPayload,
  TeamPayload,
} from "@/lib/types";

// Team members and per-team member counts are derived client-side from the
// users list (there is no member-list endpoint), so membership mutations
// invalidate ["users"], not ["teams"].

export function useCreateTeam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: TeamPayload) =>
      (await api.post("/teams/", payload)).data as Team,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      // The backend auto-enrols the creating admin as a leader, so the derived
      // member data in the users list changes too.
      qc.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useUpdateTeam(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: TeamPayload) =>
      (await api.patch(`/teams/${id}/`, payload)).data as Team,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      // team_name is echoed in the users-derived membership data.
      qc.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useDeleteTeam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/teams/${id}/`);
      return id;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      qc.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useAddMember(teamId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: TeamMemberPayload) =>
      (await api.post(`/teams/${teamId}/members/`, payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateMemberRole(teamId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ userId, role }: { userId: number; role: Role }) =>
      (await api.patch(`/teams/${teamId}/members/${userId}/`, { role })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useRemoveMember(teamId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (userId: number) => {
      await api.delete(`/teams/${teamId}/members/${userId}/`);
      return userId;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useCreateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: DepartmentPayload) =>
      (await api.post("/departments/", payload)).data as Department,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["departments"] }),
  });
}

export function useUpdateDepartment(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: DepartmentPayload) =>
      (await api.patch(`/departments/${id}/`, payload)).data as Department,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["departments"] }),
  });
}

export function useDeleteDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/departments/${id}/`);
      return id;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["departments"] });
      qc.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}
