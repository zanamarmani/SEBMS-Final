"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  Alert,
  Button,
  Card,
  Spinner,
  StatCard,
} from "@/components/ui";
import { api } from "@/lib/api";
import { billGenerationMessage, type BillGenerationResult } from "@/lib/bill-generation";
import { firebaseSyncMessage, type FirebaseSyncResult } from "@/lib/firebase-sync";
import { errorMessage } from "@/lib/format";
import type { OfficeStaffProfile, Paginated } from "@/lib/types";

interface HomeCounts {
  consumers: number | null;
  unpaidBills: number | null;
  payments: number | null;
  profile: OfficeStaffProfile | null;
}

export default function OfficeHomePage() {
  const [counts, setCounts] = useState<HomeCounts>({
    consumers: null,
    unpaidBills: null,
    payments: null,
    profile: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [taskNotice, setTaskNotice] = useState("");
  const [taskError, setTaskError] = useState("");
  const [taskBusy, setTaskBusy] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.allSettled([
      api<Paginated<unknown>>("/consumers/?page_size=1"),
      api<Paginated<unknown>>("/bills/?paid=false&page_size=1"),
      api<Paginated<unknown>>("/payments/?page_size=1"),
      api<OfficeStaffProfile>("/office-staff/me/"),
    ])
      .then(([consumers, bills, payments, profile]) => {
        setCounts({
          consumers:
            consumers.status === "fulfilled" ? consumers.value.count : null,
          unpaidBills: bills.status === "fulfilled" ? bills.value.count : null,
          payments:
            payments.status === "fulfilled" ? payments.value.count : null,
          profile: profile.status === "fulfilled" ? profile.value : null,
        });
        const failed = [consumers, bills, payments, profile].find(
          (r) => r.status === "rejected",
        );
        if (failed) {
          setError(
            errorMessage((failed as PromiseRejectedResult).reason),
          );
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function runTask(key: string, path: string) {
    setTaskBusy(key);
    setTaskError("");
    setTaskNotice("");
    try {
      if (key === "sync") {
        const result = await api<FirebaseSyncResult>(path, { method: "POST" });
        setTaskNotice(firebaseSyncMessage(result));
        load();
        return;
      }
      const result = await api<BillGenerationResult>(path, { method: "POST" });
      setTaskNotice(billGenerationMessage(result));
      load();
    } catch (err) {
      setTaskError(errorMessage(err));
    } finally {
      setTaskBusy("");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">Office</h1>
      {taskNotice && <Alert tone="success">{taskNotice}</Alert>}
      {taskError && <Alert>{taskError}</Alert>}
      {error && <Alert tone="warn">{error}</Alert>}

      {loading ? (
        <Spinner />
      ) : (
        <div className="grid gap-3 sm:grid-cols-3">
          <StatCard
            label="Consumers"
            value={counts.consumers ?? "—"}
            hint="Registered in the system"
          />
          <StatCard
            label="Unpaid bills"
            value={counts.unpaidBills ?? "—"}
            hint="Awaiting payment"
            tone="amber"
          />
          <StatCard
            label="Payment records"
            value={counts.payments ?? "—"}
            hint="All gateway transactions"
            tone="green"
          />
        </div>
      )}

      <div className="grid gap-3 lg:grid-cols-2">
        <Card
          title="Quick actions"
          description="Import scanner readings and generate bills."
        >
          <div className="flex flex-wrap gap-2">
            <Button
              loading={taskBusy === "sync"}
              onClick={() =>
                void runTask("sync", "/meter-readings/sync/")
              }
            >
              Sync readings → Firebase
            </Button>
            <Button
              variant="secondary"
              loading={taskBusy === "bills"}
              onClick={() =>
                void runTask("bills", "/bills/generate/")
              }
            >
              Generate monthly bills
            </Button>
            <Link href="/reader">
              <Button variant="ghost">Capture a reading →</Button>
            </Link>
          </div>
        </Card>

        <Card title="My profile" description="Office staff record.">
          {counts.profile ? (
            <dl className="grid grid-cols-2 gap-2 text-sm">
              <dt className="text-gray-500">Name</dt>
              <dd className="text-gray-800">
                {[counts.profile.first_name, counts.profile.last_name]
                  .filter(Boolean)
                  .join(" ") || "—"}
              </dd>
              <dt className="text-gray-500">Office</dt>
              <dd className="text-gray-800">
                {counts.profile.office_location ?? "—"}
              </dd>
              <dt className="text-gray-500">Joined</dt>
              <dd className="text-gray-800">
                {counts.profile.joining_date?.slice(0, 10) ?? "—"}
              </dd>
            </dl>
          ) : (
            <p className="text-sm text-gray-500">No profile record.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
