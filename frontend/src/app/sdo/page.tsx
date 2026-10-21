"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card, Spinner, StatCard } from "@/components/ui";
import { api } from "@/lib/api";
import { errorMessage } from "@/lib/format";
import type { DashboardStats } from "@/lib/types";

export default function SdoDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<DashboardStats>("/dashboard/stats/")
      .then(setStats)
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">SDO Dashboard</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading ? (
        <Spinner />
      ) : (
        stats && (
          <>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                label="Users"
                value={stats.users.total}
                hint={`${stats.users.sdo} SDO · ${stats.users.office_staff} office · ${stats.users.meter_reader} readers · ${stats.users.consumer} consumers`}
                tone="blue"
              />
              <StatCard
                label="Consumers"
                value={stats.consumers.total}
                hint={`${stats.consumers.approved_count} approved · ${stats.consumers.pending_count} pending`}
                tone={stats.consumers.pending_count > 0 ? "amber" : "green"}
              />
              <StatCard
                label="Bills"
                value={stats.bills.total}
                hint={`${stats.bills.paid_count} paid · ${stats.bills.unpaid_count} unpaid`}
                tone="gray"
              />
              <StatCard
                label="Collected"
                value={
                  stats.bills.total_collected
                    ? `Rs ${Number(stats.bills.total_collected).toLocaleString("en-PK")}`
                    : "—"
                }
                hint={`${stats.payments.total_success} successful payments`}
                tone="green"
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <Card
                title="Pending approvals"
                description="Consumers waiting for SDO approval"
              >
                {stats.consumers.pending_count > 0 ? (
                  <Link
                    href="/sdo/consumers?filter=pending"
                    className="text-sm font-medium text-blue-600 hover:underline"
                  >
                    Review {stats.consumers.pending_count} pending →
                  </Link>
                ) : (
                  <p className="text-sm text-gray-500">Nothing pending. 🎉</p>
                )}
              </Card>
              <Card title="Tariff slabs">
                <Link
                  href="/sdo/tariffs"
                  className="text-sm font-medium text-blue-600 hover:underline"
                >
                  Manage tariff plans →
                </Link>
              </Card>
              <Card title="Staff accounts">
                <Link
                  href="/sdo/users"
                  className="text-sm font-medium text-blue-600 hover:underline"
                >
                  Manage users & roles →
                </Link>
              </Card>
            </div>
          </>
        )
      )}
    </div>
  );
}
