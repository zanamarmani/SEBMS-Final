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
  StatCard,
  Table,
  Td,
} from "@/components/ui";
import { api } from "@/lib/api";
import { dateOnly, errorMessage, money } from "@/lib/format";
import type {
  Bill,
  Consumer,
  CursorPaginated,
  Meter,
  Paginated,
  Payment,
  PaymentInitiate,
  PaymentResult,
} from "@/lib/types";

export default function ConsumerDashboardPage() {
  const [profile, setProfile] = useState<Consumer | null>(null);
  const [profileError, setProfileError] = useState("");
  const [meters, setMeters] = useState<Meter[]>([]);
  const [bills, setBills] = useState<Bill[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [prev, setPrev] = useState<string | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editName, setEditName] = useState("");
  const [editAddress, setEditAddress] = useState("");
  const [editBusy, setEditBusy] = useState(false);
  const [editNotice, setEditNotice] = useState("");
  const [editErrors, setEditErrors] = useState<Record<string, string>>({});

  const [payBusy, setPayBusy] = useState<number | null>(null);
  const [payResult, setPayResult] = useState<
    { tone: "success" | "error"; text: string } | null
  >(null);

  const loadBills = useCallback((url?: string | null) => {
    const path = url ?? "/bills/?page_size=10";
    api<CursorPaginated<Bill>>(path)
      .then((env) => {
        setBills(env.results);
        setNext(env.next);
        setPrev(env.previous);
      })
      .catch(() => setBills([]));
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.allSettled([
      api<Consumer>("/consumers/me/"),
      api<Meter[] | { results: Meter[] }>("/meters/me/"),
      api<Payment[]>("/payments/?page_size=10").catch(() => null),
    ])
      .then(([meRes, metersRes, payRes]) => {
        if (meRes.status === "fulfilled") {
          setProfile(meRes.value);
          setEditName(meRes.value.consumer_name);
          setEditAddress(meRes.value.consumer_address);
        } else {
          setProfileError(errorMessage(meRes.reason));
        }
        if (metersRes.status === "fulfilled") {
          const val = metersRes.value;
          setMeters(Array.isArray(val) ? val : val.results);
        }
        if (payRes.status === "fulfilled" && payRes.value) {
          const val = payRes.value as Payment[] | Paginated<Payment>;
          setPayments(Array.isArray(val) ? val : val.results);
        }
        loadBills();
      })
      .finally(() => setLoading(false));
  }, [loadBills]);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setEditBusy(true);
    setEditErrors({});
    setEditNotice("");
    setError("");
    try {
      const updated = await api<Consumer>("/consumers/me/", {
        method: "PATCH",
        body: {
          consumer_name: editName,
          consumer_address: editAddress,
        },
      });
      setProfile((p) => (p ? { ...p, ...updated } : updated));
      setEditNotice("Profile updated.");
    } catch (err) {
      const fe: Record<string, string> = {};
      const details = (err as { details?: unknown }).details;
      if (details && typeof details === "object") {
        for (const [k, v] of Object.entries(
          details as Record<string, unknown>,
        )) {
          if (Array.isArray(v)) fe[k] = v.map(String).join(" ");
        }
      }
      setEditErrors(
        Object.keys(fe).length ? fe : { non_field: errorMessage(err) },
      );
    } finally {
      setEditBusy(false);
    }
  }

  async function pay(bill: Bill) {
    setPayBusy(bill.id);
    setPayResult(null);
    setError("");
    try {
      const initiated = await api<PaymentInitiate>(
        `/payments/initiate/${bill.id}/`,
        { method: "POST" },
      );

      if (initiated.mode === "mock") {
        const result = await api<PaymentResult>("/payments/callback/", {
          method: "POST",
          auth: false,
          body: initiated.mock_callback_hint.body,
        });
        if (result.status === "success") {
          setPayResult({
            tone: "success",
            text: `Payment successful for bill #${bill.id} (${result.detail})`,
          });
        } else {
          setPayResult({
            tone: "error",
            text: `Payment failed for bill #${bill.id}: ${result.detail}`,
          });
        }
        load();
      } else {
        setPayResult({
          tone: "success",
          text: `Gateway payload ready (${initiated.gateway_url}). Redirecting…`,
        });
        const form = document.createElement("form");
        form.method = "POST";
        form.action = initiated.gateway_url;
        for (const [k, v] of Object.entries(initiated.gateway_payload)) {
          const input = document.createElement("input");
          input.type = "hidden";
          input.name = k;
          input.value = String(v);
          form.appendChild(input);
        }
        document.body.appendChild(form);
        form.submit();
      }
    } catch (err) {
      setPayResult({ tone: "error", text: errorMessage(err) });
    } finally {
      setPayBusy(null);
    }
  }

  if (loading) return <Spinner label="Loading your dashboard…" />;

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-gray-900">My dashboard</h1>

      {payResult && (
        <Alert tone={payResult.tone === "success" ? "success" : "error"}>
          {payResult.text}
        </Alert>
      )}
      {error && <Alert>{error}</Alert>}

      {!profile ? (
        <Alert tone="warn">
          {profileError ||
            "No consumer profile is linked to this account. Contact the office."}
        </Alert>
      ) : (
        <div className="grid gap-3 sm:grid-cols-3">
          <StatCard
            label="Consumer #"
            value={profile.consumer_number}
            hint={profile.consumer_division ?? undefined}
          />
          <StatCard
            label="Tariff"
            value={profile.consumer_tariff_detail?.tariff_type ?? "—"}
            hint={
              profile.consumer_tariff_detail
                ? `first 100 @ ${money(profile.consumer_tariff_detail.price_100)}`
                : undefined
            }
            tone="green"
          />
          <StatCard
            label="Status"
            value={profile.approved ? "Approved" : "Pending"}
            hint="Approval by SDO"
            tone={profile.approved ? "green" : "amber"}
          />
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="My meters">
          {meters.length === 0 ? (
            <p className="text-sm text-gray-500">
              No meters assigned yet. Contact the office.
            </p>
          ) : (
            <Table head={["Meter #", "Type", "Consumer"]}>
              {meters.map((m) => (
                <tr key={m.id}>
                  <Td className="font-medium">{m.meter_number ?? "—"}</Td>
                  <Td>{m.meter_type ?? "—"}</Td>
                  <Td>{m.consumer_detail?.consumer_name ?? "—"}</Td>
                </tr>
              ))}
            </Table>
          )}
        </Card>

        {profile && (
          <Card title="Edit my details" description="Name and address only.">
            {editNotice && (
              <p className="mb-2 text-sm text-green-700">{editNotice}</p>
            )}
            <form onSubmit={(e) => void saveProfile(e)} className="space-y-3">
              <Field label="Name" error={editErrors.consumer_name}>
                <Input
                  value={editName ?? ""}
                  onChange={(e) => setEditName(e.target.value)}
                />
              </Field>
              <Field label="Address" error={editErrors.consumer_address}>
                <Input
                  value={editAddress ?? ""}
                  onChange={(e) => setEditAddress(e.target.value)}
                />
              </Field>
              {editErrors.non_field && (
                <p className="text-sm text-red-600">{editErrors.non_field}</p>
              )}
              <Button type="submit" loading={editBusy}>
                Save
              </Button>
            </form>
          </Card>
        )}
      </div>

      <Card
        title="My bills"
        description="Cursor paginated; newest first."
        actions={
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={!prev}
              onClick={() => loadBills(prev)}
            >
              ← Prev
            </Button>
            <Button
              variant="secondary"
              disabled={!next}
              onClick={() => loadBills(next)}
            >
              Next →
            </Button>
          </div>
        }
      >
        <Table
          head={[
            "#",
            "Month",
            "Due",
            "Units",
            "Payable",
            "After due",
            "Status",
            "",
          ]}
          empty={bills.length === 0}
        >
          {bills.map((b) => (
            <tr key={b.id}>
              <Td>{b.id}</Td>
              <Td>{dateOnly(b.billmonth)}</Td>
              <Td>{dateOnly(b.duedate)}</Td>
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
              <Td className="text-right">
                {!b.paid && (
                  <Button
                    className="px-2 py-1 text-xs"
                    loading={payBusy === b.id}
                    onClick={() => void pay(b)}
                  >
                    Pay {money(b.payableamount)}
                  </Button>
                )}
              </Td>
            </tr>
          ))}
        </Table>
      </Card>

      <Card title="Payment history">
        <Table
          head={["When", "Bill", "Amount", "Reference", "Status"]}
          empty={payments.length === 0}
        >
          {payments.map((p) => (
            <tr key={p.id}>
              <Td>{p.created_at.replace("T", " ").slice(0, 16)}</Td>
              <Td>#{p.bill ?? "—"}</Td>
              <Td>{money(p.amount)}</Td>
              <Td className="font-mono text-xs">{p.reference ?? "—"}</Td>
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
      </Card>
    </div>
  );
}
