"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import Header from "@/components/Header";
import { Card } from "@/components/ui/Card";
import { STATUS_LABELS } from "@/lib/labels";
import { useProfile, useRequireAuth } from "@/lib/hooks";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { useTaskStats } from "@/lib/stats";
import { TaskStatus } from "@/lib/types";

// Semantic status colours (chip text tones) — the only colour on the page.
const STATUS_COLORS: Record<TaskStatus, string> = {
  new: "#4b5563",
  in_progress: "#a65a0b",
  done: "#067a54",
  overdue: "#c7362b",
};

const BAR_COLOR = "#14151a";
const GRID_COLOR = "#eaeaec";

export default function DashboardPage() {
  const { data: stats, isPending, isError } = useTaskStats();
  useRequireAuth(isError);

  const { data: me } = useProfile();
  const isAdmin = me?.is_admin ?? false;
  const { data: users } = useUsers(isAdmin);
  const { data: teams } = useTeams(isAdmin);
  const { data: departments } = useDepartments(isAdmin);

  function userName(id: number): string {
    if (me && id === me.id)
      return `${me.last_name} ${me.first_name}`.trim() || me.username;
    const u = users?.find((u) => u.id === id);
    return u ? `${u.last_name} ${u.first_name}`.trim() || u.username : `User #${id}`;
  }

  function teamName(id: number): string {
    const fromProfile = me?.memberships.find((m) => m.team === id)?.team_name;
    return fromProfile ?? teams?.find((t) => t.id === id)?.name ?? `Nhóm #${id}`;
  }

  function departmentName(id: number): string {
    return departments?.find((d) => d.id === id)?.name ?? `Phòng #${id}`;
  }

  if (isPending || isError || !stats) {
    return (
      <main className="min-h-screen">
        <Header />
        <p className="py-16 text-center text-sm text-muted">Đang tải…</p>
      </main>
    );
  }

  const statusData = (
    Object.entries(stats.by_status) as [TaskStatus, number][]
  ).map(([status, count]) => ({
    status,
    name: STATUS_LABELS[status],
    count,
  }));

  const userData = stats.by_assignee_user.map((row) => ({
    name: userName(row.assignee_user_id),
    count: row.count,
  }));

  const teamData = stats.by_team.map((row) => ({
    name: teamName(row.assignee_team_id),
    count: row.count,
  }));

  const departmentData = stats.by_department.map((row) => ({
    name: departmentName(row.assignee_department_id),
    count: row.count,
  }));

  const nonZeroStatus = statusData.filter((r) => r.count > 0);

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        <h1 className="text-lg font-semibold tracking-tight">Dashboard</h1>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          <StatCard label="Tổng" value={stats.total} />
          {statusData.map((row) => (
            <StatCard
              key={row.status}
              label={row.name}
              value={row.count}
              dot={STATUS_COLORS[row.status]}
              emphasize={row.status === "overdue"}
            />
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <ChartCard title="Theo trạng thái">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={nonZeroStatus}
                  dataKey="count"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={90}
                  paddingAngle={2}
                  isAnimationActive={false}
                >
                  {nonZeroStatus.map((row) => (
                    <Cell key={row.status} fill={STATUS_COLORS[row.status]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Theo người phụ trách">
            <StatsBarChart data={userData} />
          </ChartCard>

          <ChartCard title="Theo nhóm">
            <StatsBarChart data={teamData} />
          </ChartCard>

          <ChartCard title="Theo phòng ban">
            <StatsBarChart data={departmentData} />
          </ChartCard>
        </div>
      </div>
    </main>
  );
}

function StatCard({
  label,
  value,
  dot,
  emphasize,
}: {
  label: string;
  value: number;
  dot?: string;
  emphasize?: boolean;
}) {
  return (
    <Card className="p-4">
      <p className="flex items-center gap-1.5 text-xs text-muted">
        {dot && (
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ background: dot }}
          />
        )}
        {label}
      </p>
      <p
        className="mt-1 text-2xl font-semibold tabular-nums tracking-tight"
        style={emphasize ? { color: "#c7362b" } : undefined}
      >
        {value}
      </p>
    </Card>
  );
}

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-4">
      <h2 className="text-[13px] font-medium text-muted">{title}</h2>
      <div className="mt-3">{children}</div>
    </Card>
  );
}

function StatsBarChart({ data }: { data: { name: string; count: number }[] }) {
  if (data.length === 0) {
    return (
      <p className="py-10 text-center text-sm text-muted">Chưa có dữ liệu.</p>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 8 }}>
        <CartesianGrid stroke={GRID_COLOR} vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 12, fill: "#565962" }}
          stroke={GRID_COLOR}
        />
        <YAxis
          allowDecimals={false}
          tick={{ fontSize: 12, fill: "#565962" }}
          stroke={GRID_COLOR}
        />
        <Tooltip cursor={{ fill: "rgba(20,21,26,.04)" }} />
        <Bar
          dataKey="count"
          name="Số công việc"
          fill={BAR_COLOR}
          radius={[4, 4, 0, 0]}
          isAnimationActive={false}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
