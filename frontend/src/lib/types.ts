export interface TeamMembership {
  team: number;
  team_name: string;
  role: "leader" | "member";
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  memberships: TeamMembership[];
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
}
