"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Alert,
  Badge,
  Button,
  Card,
  Field,
  Input,
  Spinner,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { errorMessage, fieldErrors, money } from "@/lib/format";
import type { Tariff, TariffType } from "@/lib/types";

const TYPES: { value: TariffType; label: string }[] = [
  { value: "domestic", label: "Domestic" },
  { value: "commercial", label: "Commercial" },
  { value: "industrial", label: "Industrial" },
];

const EMPTY_PRICES = {
  price_100: "",
  price_200: "",
  price_300: "",
  price_above: "",
};

export default function TariffsPage() {
  const [tariffs, setTariffs] = useState<Tariff[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    tariff_type: "domestic",
    ...EMPTY_PRICES,
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editPrices, setEditPrices] = useState({ ...EMPTY_PRICES });
  const [editErrors, setEditErrors] = useState<Record<string, string>>({});

  const load = useCallback(() => {
    api<{ results: Tariff[] }>("/tariffs/")
      .then((env) => setTariffs(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setFormErrors({});
    try {
      await api("/tariffs/", {
        method: "POST",
        body: {
          tariff_type: form.tariff_type,
          price_100: form.price_100,
          price_200: form.price_200,
          price_300: form.price_300,
          price_above: form.price_above,
        },
      });
      setForm({ tariff_type: "domestic", ...EMPTY_PRICES });
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

  async function saveEdit(id: number) {
    setBusy(true);
    setEditErrors({});
    try {
      await api(`/tariffs/${id}/`, { method: "PATCH", body: editPrices });
      setEditingId(null);
      load();
    } catch (err) {
      const fe = fieldErrors(err);
      setEditErrors(
        Object.keys(fe).length ? fe : { non_field: errorMessage(err) },
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">Tariffs</h1>
      {error && <Alert>{error}</Alert>}

      <Card
        title="Create tariff"
        description="One plan per type; prices are Rs per 100-unit slab."
      >
        <form onSubmit={(e) => void create(e)} className="space-y-3">
          {formErrors.non_field && <Alert>{formErrors.non_field}</Alert>}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <Field label="Type" required>
              <select
                className="block w-full rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm"
                value={form.tariff_type}
                onChange={(e) =>
                  setForm((f) => ({ ...f, tariff_type: e.target.value }))
                }
              >
                {TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </Field>
            {(
              [
                ["price_100", "0–100"],
                ["price_200", "101–200"],
                ["price_300", "201–300"],
                ["price_above", "301+"],
              ] as const
            ).map(([key, label]) => (
              <Field key={key} label={label} required error={formErrors[key]}>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={form[key]}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, [key]: e.target.value }))
                  }
                  required
                />
              </Field>
            ))}
          </div>
          <Button type="submit" loading={busy}>
            Add tariff
          </Button>
        </form>
      </Card>

      <Card title="Current tariffs">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            head={["Type", "0–100", "101–200", "201–300", "301+", ""]}
            empty={tariffs.length === 0}
          >
            {tariffs.map((t) => (
              <tr key={t.id}>
                <Td>
                  <Badge tone="blue">{t.tariff_type}</Badge>
                </Td>
                <Td>{money(t.price_100)}</Td>
                <Td>{money(t.price_200)}</Td>
                <Td>{money(t.price_300)}</Td>
                <Td>{money(t.price_above)}</Td>
                <Td className="text-right">
                  {editingId === t.id ? (
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        onClick={() => setEditingId(null)}
                      >
                        Cancel
                      </Button>
                      <Button
                        loading={busy}
                        onClick={() => void saveEdit(t.id)}
                      >
                        Save
                      </Button>
                    </div>
                  ) : (
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setEditingId(t.id);
                        setEditErrors({});
                        setEditPrices({
                          price_100: t.price_100,
                          price_200: t.price_200,
                          price_300: t.price_300,
                          price_above: t.price_above,
                        });
                      }}
                    >
                      Edit prices
                    </Button>
                  )}
                </Td>
              </tr>
            ))}
          </Table>
        )}
        {editingId !== null && (
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3">
            <p className="mb-2 text-xs font-semibold text-amber-800">
              Editing slab prices #{editingId}
            </p>
            {editErrors.non_field && (
              <p className="mb-2 text-xs text-red-600">{editErrors.non_field}</p>
            )}
            <div className="grid gap-3 sm:grid-cols-4">
              {(
                [
                  ["price_100", "0–100"],
                  ["price_200", "101–200"],
                  ["price_300", "201–300"],
                  ["price_above", "301+"],
                ] as const
              ).map(([key, label]) => (
                <Field key={key} label={label} error={editErrors[key]}>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={editPrices[key]}
                    onChange={(e) =>
                      setEditPrices((p) => ({ ...p, [key]: e.target.value }))
                    }
                  />
                </Field>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
