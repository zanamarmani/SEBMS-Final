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
import { firebaseSyncMessage, type FirebaseSyncResult } from "@/lib/firebase-sync";
import { dateOnly, errorMessage, unitsBetween } from "@/lib/format";
import type { MeterReading, Paginated } from "@/lib/types";

const MEDIA_ORIGIN =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1").replace(
    /\/api\/v1\/?$/,
    "",
  );

export default function OfficeReadingsPage() {
  const [readings, setReadings] = useState<MeterReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [processed, setProcessed] = useState("");
  const [taskBusy, setTaskBusy] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page_size: "50" });
    if (processed) params.set("processed", processed);
    api<Paginated<MeterReading>>(`/meter-readings/?${params.toString()}`)
      .then((env) => setReadings(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [processed]);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function sync() {
    setTaskBusy(true);
    setNotice("");
    setError("");
    try {
      const res = await api<FirebaseSyncResult>(
        "/meter-readings/sync/",
        { method: "POST" },
      );
      setNotice(firebaseSyncMessage(res));
      load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setTaskBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">
          Meter readings
        </h1>
        <Button loading={taskBusy} onClick={() => void sync()}>
          Sync from Firebase
        </Button>
      </div>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card title="Filters">
        <div className="flex items-end gap-3">
          <div>
            <p className="mb-1 text-xs font-medium text-gray-500">Processed</p>
            <Select
              value={processed}
              onChange={(e) => setProcessed(e.target.value)}
              className="w-44"
            >
              <option value="">All</option>
              <option value="true">Processed (billed)</option>
              <option value="false">Unprocessed</option>
            </Select>
          </div>
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        </div>
      </Card>

      <Card title="Readings">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={[
              "Date",
              "Meter",
              "Last → New",
              "Units",
              "Status",
              "Processed",
              "Photo",
            ]}
            empty={readings.length === 0}
          >
            {readings.map((r) => (
              <tr key={r.id}>
                <Td>{dateOnly(r.reading_date)}</Td>
                <Td className="font-medium">{r.meter_number ?? "—"}</Td>
                <Td>
                  {r.last_reading ?? "—"} → {r.new_reading ?? "—"}
                </Td>
                <Td>{unitsBetween(r.last_reading, r.new_reading)}</Td>
                <Td>
                  {r.meter_status ? (
                    <Badge tone="green">Active</Badge>
                  ) : (
                    <Badge tone="red">Inactive</Badge>
                  )}
                </Td>
                <Td>
                  {r.processed ? (
                    <Badge tone="blue">Billed</Badge>
                  ) : (
                    <Badge tone="amber">Pending</Badge>
                  )}
                </Td>
                <Td>
                  {r.meter_image ? (
                    <a
                      href={`${MEDIA_ORIGIN}${r.meter_image}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      view
                    </a>
                  ) : (
                    "—"
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
