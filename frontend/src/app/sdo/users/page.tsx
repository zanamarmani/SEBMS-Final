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
import type { Paginated, Role, User } from "@/lib/types";

const ROLES: { value: Role; label: string }[] = [
  { value: "sdo", label: "SDO" },
  { value: "office_staff", label: "Office staff" },
  { value: "meter_reader", label: "Meter reader" },
  { value: "consumer", label: "Consumer" },
];

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [form, setForm] = useState({
    email: "",
    password: "",
    role: "office_staff",
    is_active: true,
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    api<Paginated<User>>("/users/?page_size=50")
      .then((env) => setUsers(env.results))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setFormErrors({});
    setNotice("");
    try {
      await api("/users/", { method: "POST", body: form });
      setForm({ email: "", password: "", role: "office_staff", is_active: true });
      setNotice("User created.");
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

  async function toggleActive(u: User) {
    setNotice("");
    setError("");
    try {
      await api(`/users/${u.id}/`, {
        method: "PATCH",
        body: { is_active: !u.is_active },
      });
      setNotice(`${u.email} ${u.is_active ? "deactivated" : "activated"}.`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function remove(u: User) {
    if (!confirm(`Delete user ${u.email}?`)) return;
    setNotice("");
    setError("");
    try {
      await api(`/users/${u.id}/`, { method: "DELETE" });
      setNotice(`Deleted ${u.email}.`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">Users</h1>
      {notice && <Alert tone="success">{notice}</Alert>}
      {error && <Alert>{error}</Alert>}

      <Card title="Create user" description="Staff & internal accounts.">
        <form onSubmit={(e) => void create(e)} className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Field label="Email" required error={formErrors.email}>
              <Input
                type="email"
                value={form.email}
                onChange={(e) =>
                  setForm((f) => ({ ...f, email: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Password" required error={formErrors.password}>
              <Input
                type="password"
                value={form.password}
                onChange={(e) =>
                  setForm((f) => ({ ...f, password: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Role" required error={formErrors.role}>
              <Select
                value={form.role}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    role: e.target.value as Role,
                  }))
                }
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Active">
              <label className="flex h-9 items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, is_active: e.target.checked }))
                  }
                />
                Enabled
              </label>
            </Field>
          </div>
          {formErrors.non_field && <Alert>{formErrors.non_field}</Alert>}
          <Button type="submit" loading={busy}>
            Create user
          </Button>
        </form>
      </Card>

      <Card title="All users">
        {loading ? (
          <Spinner />
        ) : (
          <Table head={["Email", "Role", "Status", "Actions"]} empty={users.length === 0}>
            {users.map((u) => (
              <tr key={u.id}>
                <Td className="font-medium">{u.email}</Td>
                <Td>
                  <Badge tone={u.role ? "blue" : "amber"}>
                    {u.is_superuser ? "superuser" : (u.role ?? "no role")}
                  </Badge>
                </Td>
                <Td>
                  {u.is_active ? (
                    <Badge tone="green">Active</Badge>
                  ) : (
                    <Badge tone="red">Disabled</Badge>
                  )}
                </Td>
                <Td>
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      className="px-2 py-1 text-xs"
                      onClick={() => void toggleActive(u)}
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    <Button
                      variant="danger"
                      className="px-2 py-1 text-xs"
                      onClick={() => void remove(u)}
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
