"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Alert, Card, Spinner, StatCard } from "@/components/ui";
import Icon from "@/components/Icon";
import { api } from "@/lib/api";
import { errorMessage } from "@/lib/format";
import type { DashboardStats } from "@/lib/types";
export default function SdoDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    api<DashboardStats>("/dashboard/stats/")
      .then((d) => {
        if (active) setStats(d);
      })
      .catch((e) => {
        if (active) setError(errorMessage(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  const paidPercent =
    stats && stats.bills.total > 0
      ? Math.round((stats.bills.paid_count / stats.bills.total) * 100)
      : 0;
  return (
    <div>
      <div className="dashboard-heading">
        <div>
          <p className="page-eyebrow">SDO workspace</p>
          <h1 className="page-heading">Your operations, at a glance.</h1>
          <p className="page-description">
            A clear view of your consumers, billing and team.
          </p>
        </div>
        <span className="period-label">Overview · All records</span>
      </div>
      {error && <Alert>{error}</Alert>}
      {loading ? (
        <Spinner label="Loading your overview…" />
      ) : (
        stats && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="Total consumers"
                value={stats.consumers.total}
                hint={`${stats.consumers.approved_count} approved · ${stats.consumers.pending_count} pending`}
                tone="blue"
              />
              <StatCard
                label="Bills issued"
                value={stats.bills.total}
                hint={`${stats.bills.paid_count} paid · ${stats.bills.unpaid_count} unpaid`}
                tone="gray"
              />
              <StatCard
                label="Payments collected"
                value={`Rs ${Number(stats.bills.total_collected || 0).toLocaleString("en-PK")}`}
                hint={`${stats.payments.total_success} successful payments`}
                tone="green"
              />
              <StatCard
                label="Registered users"
                value={stats.users.total}
                hint={`${stats.users.office_staff} office staff · ${stats.users.meter_reader} readers`}
                tone="amber"
              />
            </div>
            <div className="dashboard-grid">
              <Card
                title="Billing overview"
                description="Payment status across all issued bills"
              >
                <div className="billing-distribution">
                  <div
                    className="bill-donut"
                    role="img"
                    aria-label={`${stats.bills.paid_count} paid and ${stats.bills.unpaid_count} unpaid bills`}
                    style={{
                      background: stats.bills.total
                        ? `conic-gradient(#138e83 0 ${paidPercent}%, #e8edf3 ${paidPercent}% 100%)`
                        : "#e8edf3",
                    }}
                  >
                    <div>
                      <strong>
                        {stats.bills.total ? `${paidPercent}%` : "—"}
                      </strong>
                      <span>
                        {stats.bills.total ? "bills paid" : "No bills yet"}
                      </span>
                    </div>
                  </div>
                  <div className="legend">
                    <div>
                      <span>
                        <i style={{ background: "#138e83" }} />
                        Paid bills
                      </span>
                      <strong>{stats.bills.paid_count}</strong>
                    </div>
                    <div>
                      <span>
                        <i style={{ background: "#dce4ed" }} />
                        Unpaid bills
                      </span>
                      <strong>{stats.bills.unpaid_count}</strong>
                    </div>
                    <p className="page-description">
                      {stats.bills.total
                        ? "Based on all bills currently in the system."
                        : "Your billing summary will appear when bills are generated."}
                    </p>
                  </div>
                </div>
              </Card>
              <Card
                title="Quick access"
                description="Keep your daily operations moving"
              >
                {[
                  [
                    "users",
                    "Consumer approvals",
                    `${stats.consumers.pending_count} applications awaiting review`,
                    "/sdo/consumers?filter=pending",
                  ],
                  [
                    "tariff",
                    "Tariff management",
                    "Manage rates for every consumer type",
                    "/sdo/tariffs",
                  ],
                  [
                    "users",
                    "Team & access",
                    "Manage staff accounts and roles",
                    "/sdo/users",
                  ],
                ].map(([icon, title, desc, href]) => (
                  <Link href={href} key={title} className="action-row">
                    <span className="action-icon">
                      <Icon name={icon} />
                    </span>
                    <div>
                      <strong>{title}</strong>
                      <p>{desc}</p>
                    </div>
                    <Icon name="arrow" size={16} />
                  </Link>
                ))}
              </Card>
            </div>
            <div className="dashboard-banner">
              <span className="action-icon">
                <Icon name="shield" size={24} />
              </span>
              <div>
                <h2>
                  {stats.consumers.pending_count
                    ? "A few consumers need your attention."
                    : "You're all caught up on approvals."}
                </h2>
                <p>
                  {stats.consumers.pending_count
                    ? "Review pending registrations to help consumers get started."
                    : "New consumer registrations will appear here when they need your review."}
                </p>
              </div>
              <Link href="/sdo/consumers">View consumers →</Link>
            </div>
          </>
        )
      )}
    </div>
  );
}
