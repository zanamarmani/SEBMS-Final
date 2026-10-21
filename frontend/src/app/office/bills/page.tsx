"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Alert,
  Badge,
  Button,
  Card,
  Select,
  Spinner,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { dateOnly, errorMessage, money } from "@/lib/format";
import type { Bill, CursorPaginated } from "@/lib/types";

export default function OfficeBillsPage() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [prev, setPrev] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [paid, setPaid] = useState("");
  const [generateBusy, setGenerateBusy] = useState(false);

  const load = useCallback((url?: string | null) => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page_size: "20" });
    if (paid) params.set("paid", paid);
    const path = url ?? `/bills/?${params.toString()}`;
    api<CursorPaginated<Bill>>(path)
      .then((env) => {
        setBills(env.results);
        setNext(env.next);
        setPrev(env.previous);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [paid]);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function generate() {
    setGenerateBusy(true);
    setNotice("");
    setError("");
    try {
      const res = await api<{ task_id: string; status: string }>(
        "/bills/generate/",
        { method: "POST" },
      );
      setNotice(
        `Bill generation queued (task ${res.task_id}). Requires a running Celery worker — refresh shortly.`,
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setGenerateBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Bills</h1>
        <Button loading={generateBusy} onClick={() => void generate()}>
          Generate monthly bills
        </Button>
      </div>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card title="Filters">
        <div className="flex items-end gap-3">
          <div>
            <p className="mb-1 text-xs font-medium text-gray-500">Payment status</p>
            <Select
              value={paid}
              onChange={(e) => setPaid(e.target.value)}
              className="w-44"
            >
              <option value="">All</option>
              <option value="true">Paid</option>
              <option value="false">Unpaid</option>
            </Select>
          </div>
          <Button variant="secondary" onClick={() => load()}>
            Refresh
          </Button>
        </div>
      </Card>

      <Card
        title="Bills (cursor paginated)"
        description="Newest first."
        actions={
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={!prev || loading}
              onClick={() => load(prev)}
            >
              ← Prev
            </Button>
            <Button
              variant="secondary"
              disabled={!next || loading}
              onClick={() => load(next)}
            >
              Next →
            </Button>
          </div>
        }
      >
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={[
              "#",
              "Month",
              "Due date",
              "Meter",
              "Consumer",
              "Units",
              "Payable",
              "After due",
              "Status",
            ]}
            empty={bills.length === 0}
          >
            {bills.map((b) => (
              <tr key={b.id}>
                <Td>{b.id}</Td>
                <Td>{dateOnly(b.billmonth)}</Td>
                <Td>{dateOnly(b.duedate)}</Td>
                <Td className="font-medium">
                  {b.meter_info?.meter_number ?? b.meter ?? "—"}
                </Td>
                <Td>
                  {b.meter_info
                    ? `${b.meter_info.consumer_number ?? "—"} · ${
                        b.meter_info.consumer_name ?? "—"
                      }`
                    : "—"}
                </Td>
                <Td>{b.unitsconsumed}</Td>
                <Td>{money(b.payableamount)}</Td>
                <Td>{money(b.payable_after_due_date)}</Td>
                <Td>
                  {b.paid ? (
                    <Badge tone="green">Paid</Badge>
                  ) : (
                    <Badge tone="amber">Unpaid</Badge>
                  )}
                </Td>
              </tr>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
