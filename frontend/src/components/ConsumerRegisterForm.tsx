"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { errorMessage, fieldErrors } from "@/lib/format";
import type { Division, Tariff } from "@/lib/types";
import { Alert, Button, Field, Input, Select } from "./ui";

const DIVISIONS: { value: Division; label: string }[] = [
  { value: "division1", label: "Division 1" },
  { value: "division2", label: "Division 2" },
  { value: "division3", label: "Division 3" },
];

const EMPTY = {
  email: "",
  password: "",
  consumer_number: "",
  consumer_name: "",
  consumer_address: "",
  consumer_tariff: "",
  consumer_division: "division1",
};

export default function ConsumerRegisterForm({
  onSuccess,
}: {
  onSuccess?: () => void;
}) {
  const [tariffs, setTariffs] = useState<Tariff[]>([]);
  const [form, setForm] = useState({ ...EMPTY });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [done, setDone] = useState(false);

  useEffect(() => {
    api<{ results: Tariff[] }>("/tariffs/", { auth: false })
      .then((env) => setTariffs(env.results))
      .catch(() => setTariffs([]));
  }, []);

  function set(key: keyof typeof EMPTY, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setFields({});
    try {
      await api("/consumers/register/", {
        method: "POST",
        auth: false,
        body: {
          ...form,
          consumer_tariff: Number(form.consumer_tariff),
        },
      });
      setDone(true);
      onSuccess?.();
    } catch (err) {
      const fe = fieldErrors(err);
      if (Object.keys(fe).length > 0) setFields(fe);
      else setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <Alert tone="success">
        Registration submitted. Your account is pending approval by the SDO —
        you will not be able to log in until it is approved.
      </Alert>
    );
  }

  return (
    <form onSubmit={(e) => void submit(e)} className="space-y-4">
      {error && <Alert>{error}</Alert>}
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Email" required error={fields.email}>
          <Input
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={(e) => set("email", e.target.value)}
            required
          />
        </Field>
        <Field
          label="Password"
          required
          error={fields.password}
          hint="Min. 8 characters, not entirely numeric."
        >
          <Input
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={(e) => set("password", e.target.value)}
            required
          />
        </Field>
        <Field label="Consumer number" required error={fields.consumer_number}>
          <Input
            value={form.consumer_number}
            onChange={(e) => set("consumer_number", e.target.value)}
            required
          />
        </Field>
        <Field label="Consumer name" required error={fields.consumer_name}>
          <Input
            value={form.consumer_name}
            onChange={(e) => set("consumer_name", e.target.value)}
            required
          />
        </Field>
        <Field label="Address" required error={fields.consumer_address}>
          <Input
            value={form.consumer_address}
            onChange={(e) => set("consumer_address", e.target.value)}
            required
          />
        </Field>
        <Field label="Division" required error={fields.consumer_division}>
          <Select
            value={form.consumer_division}
            onChange={(e) => set("consumer_division", e.target.value)}
          >
            {DIVISIONS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Tariff" required error={fields.consumer_tariff}>
          <Select
            value={form.consumer_tariff}
            onChange={(e) => set("consumer_tariff", e.target.value)}
            required
          >
            <option value="" disabled>
              Select tariff…
            </option>
            {tariffs.map((t) => (
              <option key={t.id} value={t.id}>
                {t.tariff_type} (first 100 @ Rs {t.price_100})
              </option>
            ))}
          </Select>
        </Field>
      </div>
      <Button type="submit" loading={busy}>
        Register
      </Button>
    </form>
  );
}
