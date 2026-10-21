"use client";

import { useCallback, useEffect, useState } from "react";

import ConsumerRegisterForm from "@/components/ConsumerRegisterForm";
import {
  Alert,
  Badge,
  Button,
  Card,
  Input,
  Select,
  Spinner,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { errorMessage } from "@/lib/format";
import type { Consumer, Paginated } from "@/lib/types";

export default function OfficeConsumersPage() {
  const [filter, setFilter] = useState("");
  const [query, setQuery] = useState("");
  const [consumers, setConsumers] = useState<Consumer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page_size: "50" });
    if (filter) params.set("approved", filter);
    if (query) params.set("search", query);
    api<Paginated<Consumer>>(`/consumers/?${params.toString()}`)
      .then((env) => setConsumers(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [filter, query]);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function action(fn: () => Promise<unknown>, message: string) {
    setNotice("");
    setError("");
    try {
      await fn();
      setNotice(message);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Consumers</h1>
        <Button onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Close form" : "Register consumer"}
        </Button>
      </div>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      {showForm && (
        <Card
          title="Register a consumer"
          description="Creates the account; SDO approval still required."
        >
          <ConsumerRegisterForm
            onSuccess={() => {
              setNotice("Registration created (pending approval).");
              setShowForm(false);
              load();
            }}
          />
        </Card>
      )}

      <Card
        title="List"
        actions={
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        }
      >
        <div className="mb-3 flex flex-wrap items-end gap-3">
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-40"
          >
            <option value="">All statuses</option>
            <option value="true">Approved</option>
            <option value="false">Pending</option>
          </Select>
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              load();
            }}
          >
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search number / name / address"
              className="w-64"
            />
            <Button variant="secondary" type="submit">
              Search
            </Button>
          </form>
        </div>
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={[
              "Number",
              "Name",
              "Email",
              "Division",
              "Tariff",
              "Meters",
              "Status",
              "Actions",
            ]}
            empty={consumers.length === 0}
          >
            {consumers.map((c) => (
              <tr key={c.id}>
                <Td className="font-medium">{c.consumer_number}</Td>
                <Td>{c.consumer_name}</Td>
                <Td>{c.user_email ?? "—"}</Td>
                <Td>{c.consumer_division ?? "—"}</Td>
                <Td>{c.consumer_tariff_detail?.tariff_type ?? "—"}</Td>
                <Td>{c.meter_numbers.join(", ") || "—"}</Td>
                <Td>
                  {c.approved ? (
                    <Badge tone="green">Approved</Badge>
                  ) : (
                    <Badge tone="amber">Pending</Badge>
                  )}
                </Td>
                <Td>
                  <Button
                    variant="danger"
                    className="px-2 py-1 text-xs"
                    onClick={() => {
                      if (confirm(`Delete consumer ${c.consumer_number}?`)) {
                        void action(
                          () => api(`/consumers/${c.id}/`, { method: "DELETE" }),
                          `Deleted ${c.consumer_number}.`,
                        );
                      }
                    }}
                  >
                    Delete
                  </Button>
                </Td>
              </tr>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
