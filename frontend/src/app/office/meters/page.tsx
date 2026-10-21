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
import { errorMessage, fieldErrors } from "@/lib/format";
import type { Consumer, Meter, MeterType, Paginated } from "@/lib/types";

const TYPES: { value: MeterType; label: string }[] = [
  { value: "single", label: "Single Phase" },
  { value: "double", label: "Double Phase" },
  { value: "three", label: "Three Phase" },
];

export default function OfficeMetersPage() {
  const [meters, setMeters] = useState<Meter[]>([]);
  const [consumers, setConsumers] = useState<Consumer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [form, setForm] = useState({
    meter_number: "",
    meter_type: "single",
    consumer: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.allSettled([
      api<Paginated<Meter>>("/meters/?page_size=100"),
      api<Paginated<Consumer>>("/consumers/?approved=true&page_size=100"),
    ])
      .then(([metersRes, consumersRes]) => {
        if (metersRes.status === "fulfilled") {
          setMeters(metersRes.value.results);
        } else {
          setError(errorMessage(metersRes.reason));
        }
        if (consumersRes.status === "fulfilled") {
          setConsumers(consumersRes.value.results);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function assign(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setFormErrors({});
    setNotice("");
    try {
      await api("/meters/", {
        method: "POST",
        body: {
          meter_number: Number(form.meter_number),
          meter_type: form.meter_type,
          consumer: form.consumer ? Number(form.consumer) : null,
        },
      });
      setForm({ meter_number: "", meter_type: "single", consumer: "" });
      setNotice("Meter assigned.");
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

  async function reassign(meter: Meter, consumerId: string) {
    setNotice("");
    setError("");
    try {
      await api(`/meters/${meter.id}/`, {
        method: "PATCH",
        body: { consumer: consumerId ? Number(consumerId) : null },
      });
      setNotice(
        `Meter ${meter.meter_number} updated.`,
      );
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function remove(meter: Meter) {
    if (!confirm(`Delete meter ${meter.meter_number}?`)) return;
    setNotice("");
    setError("");
    try {
      await api(`/meters/${meter.id}/`, { method: "DELETE" });
      setNotice(`Meter ${meter.meter_number} deleted.`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">Meters</h1>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card title="Assign meter" description="Meters require an approved consumer.">
        <form onSubmit={(e) => void assign(e)} className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-3">
            <Field label="Meter number" required error={formErrors.meter_number}>
              <Input
                type="number"
                value={form.meter_number}
                onChange={(e) =>
                  setForm((f) => ({ ...f, meter_number: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Meter type" required error={formErrors.meter_type}>
              <Select
                value={form.meter_type}
                onChange={(e) =>
                  setForm((f) => ({ ...f, meter_type: e.target.value }))
                }
              >
                {TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Consumer" error={formErrors.consumer}>
              <Select
                value={form.consumer}
                onChange={(e) =>
                  setForm((f) => ({ ...f, consumer: e.target.value }))
                }
              >
                <option value="">— Unassigned —</option>
                {consumers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.consumer_number} · {c.consumer_name}
                  </option>
                ))}
              </Select>
            </Field>
          </div>
          {formErrors.non_field && <Alert>{formErrors.non_field}</Alert>}
          <Button type="submit" loading={busy}>
            Assign meter
          </Button>
        </form>
      </Card>

      <Card title="All meters" actions={<Button variant="secondary" onClick={load}>Refresh</Button>}>
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={["Meter #", "Type", "Consumer", "Approved", "Actions"]}
            empty={meters.length === 0}
          >
            {meters.map((m) => (
              <tr key={m.id}>
                <Td className="font-medium">{m.meter_number ?? "—"}</Td>
                <Td>{m.meter_type ?? "—"}</Td>
                <Td>
                  {m.consumer_detail
                    ? `${m.consumer_detail.consumer_number} · ${m.consumer_detail.consumer_name}`
                    : "—"}
                </Td>
                <Td>
                  {m.consumer ? (
                    m.consumer_detail?.approved ? (
                      <Badge tone="green">Yes</Badge>
                    ) : (
                      <Badge tone="amber">No</Badge>
                    )
                  ) : (
                    "—"
                  )}
                </Td>
                <Td>
                  <div className="flex items-center gap-2">
                    <Select
                      className="w-56"
                      value={m.consumer ?? ""}
                      onChange={(e) => void reassign(m, e.target.value)}
                    >
                      <option value="">— Unassign —</option>
                      {consumers.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.consumer_number} · {c.consumer_name}
                        </option>
                      ))}
                    </Select>
                    <Button
                      variant="danger"
                      className="px-2 py-1 text-xs"
                      onClick={() => void remove(m)}
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
