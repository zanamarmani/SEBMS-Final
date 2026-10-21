"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import {
  Alert,
  Badge,
  Button,
  Card,
  CenteredSpinner,
  Input,
  Select,
  Spinner,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { errorMessage } from "@/lib/format";
import type { Consumer, Paginated } from "@/lib/types";

function ConsumersInner() {
  const search = useSearchParams();
  const initialFilter = search.get("filter") === "pending" ? "false" : "";

  const [filter, setFilter] = useState(initialFilter);
  const [query, setQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [consumers, setConsumers] = useState<Consumer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page_size: "50" });
    if (filter) params.set("approved", filter);
    if (searchInput) params.set("search", searchInput);
    api<Paginated<Consumer>>(`/consumers/?${params.toString()}`)
      .then((env) => setConsumers(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [filter, searchInput]);

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
      <h1 className="text-lg font-semibold text-gray-900">Consumers</h1>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card
        title="Filters"
        actions={
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        }
      >
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <p className="mb-1 text-xs font-medium text-gray-500">Status</p>
            <Select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-40"
            >
              <option value="">All</option>
              <option value="true">Approved</option>
              <option value="false">Pending</option>
            </Select>
          </div>
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setSearchInput(query.trim());
            }}
          >
            <div>
              <p className="mb-1 text-xs font-medium text-gray-500">Search</p>
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="number / name / address"
                className="w-64"
              />
            </div>
            <Button variant="secondary" type="submit">
              Search
            </Button>
          </form>
        </div>
      </Card>

      <Card title="Consumers">
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
                  <div className="flex gap-2">
                    {!c.approved && (
                      <>
                        <Button
                          className="px-2 py-1 text-xs"
                          onClick={() =>
                            action(
                              () => api(`/consumers/${c.id}/approve/`, { method: "POST" }),
                              `Approved ${c.consumer_number}.`,
                            )
                          }
                        >
                          Approve
                        </Button>
                        <Button
                          variant="danger"
                          className="px-2 py-1 text-xs"
                          onClick={() => {
                            if (
                              confirm(
                                `Reject (delete) consumer ${c.consumer_number}? This cannot be undone.`,
                              )
                            ) {
                              void action(
                                () => api(`/consumers/${c.id}/reject/`, { method: "POST" }),
                                `Rejected ${c.consumer_number}.`,
                              );
                            }
                          }}
                        >
                          Reject
                        </Button>
                      </>
                    )}
                    <Button
                      variant="ghost"
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
                  </div>
                </Td>
              </tr>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}

export default function SdoConsumersPage() {
  return (
    <Suspense fallback={<CenteredSpinner />}>
      <ConsumersInner />
    </Suspense>
  );
}
