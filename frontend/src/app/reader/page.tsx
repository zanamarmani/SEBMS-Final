"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Alert,
  Badge,
  Button,
  Card,
  Field,
  Input,
  Select,
  Spinner,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { dateOnly, errorMessage, fieldErrors, unitsBetween } from "@/lib/format";
import type { Meter, MeterReading, Paginated } from "@/lib/types";

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

export default function ReaderPage() {
  const [meters, setMeters] = useState<Meter[]>([]);
  const [readings, setReadings] = useState<MeterReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    meter: "",
    new_reading: "",
    reading_date: today,
    meter_status: true,
  });
  const [image, setImage] = useState<File | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.allSettled([
      api<Paginated<Meter>>("/meters/?page_size=100"),
      api<Paginated<MeterReading>>("/meter-readings/?page_size=10"),
    ])
      .then(([metersRes, readingsRes]) => {
        if (metersRes.status === "fulfilled") {
          setMeters(metersRes.value.results);
        } else {
          setError(errorMessage(metersRes.reason));
        }
        if (readingsRes.status === "fulfilled") {
          setReadings(readingsRes.value.results);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setFormErrors({});
    setNotice("");
    setError("");

    if (image && image.size > MAX_IMAGE_SIZE) {
      setFormErrors({ meter_image: "Image must be 5 MB or smaller." });
      setBusy(false);
      return;
    }

    try {
      const fd = new FormData();
      fd.append("meter", form.meter);
      fd.append("new_reading", form.new_reading);
      fd.append("reading_date", form.reading_date);
      fd.append("meter_status", form.meter_status ? "true" : "false");
      if (image) fd.append("meter_image", image);

      await api("/meter-readings/", { formData: fd });
      setNotice("Reading captured.");
      setForm((f) => ({ ...f, new_reading: "" }));
      setImage(null);
      load();
    } catch (err) {
      const fe = fieldErrors(err);
      setFormErrors(
        Object.keys(fe).length ? fe : { non_field: errorMessage(err) },
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">
        Capture meter reading
      </h1>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card
        title="New reading"
        description="Last reading is computed server-side; photo max 5 MB (JPG/PNG/WEBP)."
      >
        <form onSubmit={(e) => void submit(e)} className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Field label="Meter" required error={formErrors.meter}>
              <Select
                value={form.meter}
                onChange={(e) =>
                  setForm((f) => ({ ...f, meter: e.target.value }))
                }
                required
              >
                <option value="" disabled>
                  Select meter…
                </option>
                {meters.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.meter_number ?? m.id}
                    {m.consumer_detail
                      ? ` · ${m.consumer_detail.consumer_name}`
                      : ""}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="New reading" required error={formErrors.new_reading}>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={form.new_reading}
                onChange={(e) =>
                  setForm((f) => ({ ...f, new_reading: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Reading date" required error={formErrors.reading_date}>
              <Input
                type="date"
                value={form.reading_date}
                onChange={(e) =>
                  setForm((f) => ({ ...f, reading_date: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Photo" error={formErrors.meter_image}>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(e) => setImage(e.target.files?.[0] ?? null)}
                className="block w-full text-sm text-gray-600 file:mr-3 file:rounded-md file:border file:border-gray-300 file:bg-white file:px-3 file:py-1.5 file:text-sm file:font-medium hover:file:bg-gray-50"
              />
            </Field>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={form.meter_status}
              onChange={(e) =>
                setForm((f) => ({ ...f, meter_status: e.target.checked }))
              }
            />
            Meter is active / sealed
          </label>
          <Button type="submit" loading={busy}>
            Submit reading
          </Button>
        </form>
      </Card>

      <Card
        title="Recent readings"
        actions={
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        }
      >
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={["Date", "Meter", "Last → New", "Units", "Processed", "Photo"]}
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
                  {r.processed ? (
                    <Badge tone="blue">Billed</Badge>
                  ) : (
                    <Badge tone="amber">Pending</Badge>
                  )}
                </Td>
                <Td>{r.meter_image ? "Yes" : "—"}</Td>
              </tr>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
