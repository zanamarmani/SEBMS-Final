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
import { errorMessage, money } from "@/lib/format";
import type { Paginated, Payment } from "@/lib/types";

export default function OfficePaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page_size: "50" });
    if (status) params.set("status", status);
    api<Paginated<Payment>>(`/payments/?${params.toString()}`)
      .then((env) => setPayments(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [status]);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Payments</h1>
        <Button variant="secondary" onClick={load}>
          Refresh
        </Button>
      </div>
      {error && <Alert>{error}</Alert>}

      <Card title="Filter">
        <Select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="w-44"
        >
          <option value="">All statuses</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
        </Select>
      </Card>

      <Card title="Payment records">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={[
              "When",
              "Bill",
              "Amount",
              "Reference",
              "Bill paid",
              "Status",
            ]}
            empty={payments.length === 0}
          >
            {payments.map((p) => (
              <tr key={p.id}>
                <Td>{p.created_at.replace("T", " ").slice(0, 16)}</Td>
                <Td className="font-medium">#{p.bill ?? "—"}</Td>
                <Td>{money(p.amount)}</Td>
                <Td className="font-mono text-xs">{p.reference ?? "—"}</Td>
                <Td>
                  {p.bill_paid ? (
                    <Badge tone="green">Yes</Badge>
                  ) : (
                    <Badge tone="gray">No</Badge>
                  )}
                </Td>
                <Td>
                  {p.status === "success" ? (
                    <Badge tone="green">success</Badge>
                  ) : (
                    <Badge tone="red">{p.status}</Badge>
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
