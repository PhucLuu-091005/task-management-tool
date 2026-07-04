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
import { STATUS_LABELS } from "@/lib/labels";
import { useProfile, useRequireAuth } from "@/lib/hooks";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { useTaskStats } from "@/lib/stats";
import { TaskStatus } from "@/lib/types";

const STATUS_COLORS: Record<TaskStatus, string> = {
  new: "#0ea5e9",
  in_progress: "#f59e0b",
  done: "#10b981",
  overdue: "#ef4444",
};

const BAR_COLOR = "#71717a";

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
    return (
      fromProfile ?? teams?.find((t) => t.id === id)?.name ?? `Nhóm #${id}`
    );
  }

  function departmentName(id: number): string {
    return departments?.find((d) => d.id === id)?.name ?? `Phòng #${id}`;
  }

  if (isPending || isError || !stats) {
    return (
      <main className="min-h-screen">
        <Header />
        <p className="py-16 text-center text-sm text-zinc-500">Đang tải…</p>
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
        <h1 className="text-lg font-semibold">Dashboard</h1>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          <StatCard label="Tổng" value={stats.total} />
          {statusData.map((row) => (
            <StatCard
              key={row.status}
              label={row.name}
              value={row.count}
              color={STATUS_COLORS[row.status]}
            />
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ChartCard title="Theo trạng thái">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={nonZeroStatus}
                  dataKey="count"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={90}
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
  color,
}: {
  label: string;
  value: number;
  color?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold" style={color ? { color } : undefined}>
        {value}
      </p>
    </div>
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
    <section className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
      <h2 className="text-sm font-medium text-zinc-500">{title}</h2>
      <div className="mt-3">{children}</div>
    </section>
  );
}

function StatsBarChart({ data }: { data: { name: string; count: number }[] }) {
  if (data.length === 0) {
    return <p className="py-10 text-center text-sm text-zinc-500">Chưa có dữ liệu.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.3} />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip />
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
