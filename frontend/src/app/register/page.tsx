"use client";

import Link from "next/link";

import ConsumerRegisterForm from "@/components/ConsumerRegisterForm";
import { Card } from "@/components/ui";

export default function RegisterPage() {
  return (
    <main className="mx-auto w-full max-w-3xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <Link
          href="/"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Home
        </Link>
        <Link
          href="/login"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          Login
        </Link>
      </div>
      <Card
        title="Consumer registration"
        description="Create your account. The SDO must approve it before you can log in."
      >
        <ConsumerRegisterForm />
      </Card>
    </main>
  );
}
