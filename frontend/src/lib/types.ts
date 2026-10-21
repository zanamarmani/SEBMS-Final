export type Role = "sdo" | "office_staff" | "meter_reader" | "consumer";

export interface ApiErrorShape {
  code: string;
  message: string;
  details: unknown;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: ApiErrorShape | null;
}

export interface User {
  id: number;
  email: string;
  role: Role | null;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CursorPaginated<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}

export type TariffType = "domestic" | "commercial" | "industrial";

export interface Tariff {
  id: number;
  tariff_type: TariffType;
  price_100: string;
  price_200: string;
  price_300: string;
  price_above: string;
}

export type Division = "division1" | "division2" | "division3";

export interface Consumer {
  id: number;
  user_email: string | null;
  consumer_number: string;
  consumer_name: string;
  consumer_address: string;
  consumer_tariff: number | null;
  consumer_tariff_detail: Tariff | null;
  consumer_division: Division | null;
  approved: boolean;
  meter_numbers: number[];
}

export type MeterType = "single" | "double" | "three";

export interface Meter {
  id: number;
  meter_number: number | null;
  meter_type: MeterType | null;
  consumer: number | null;
  consumer_detail: {
    id: number;
    consumer_number: string;
    consumer_name: string;
    approved: boolean;
  } | null;
}

export interface MeterReading {
  id: number;
  meter: number | null;
  meter_number: number | null;
  last_reading: string | null;
  new_reading: string | null;
  meter_status: boolean;
  processed: boolean;
  reading_date: string | null;
  meter_image: string | null;
}

export interface Bill {
  id: number;
  billmonth: string;
  duedate: string;
  detectionunit: string;
  averageunit: string;
  units: string;
  unitsconsumed: string;
  payableamount: string;
  payable_after_due_date: string;
  paid: boolean;
  meter: number | null;
  meter_info: {
    id: number;
    meter_number: number;
    consumer_number: string | null;
    consumer_name: string | null;
  } | null;
}

export interface Payment {
  id: number;
  bill: number | null;
  bill_paid: boolean | null;
  bill_amount: string | null;
  reference: string | null;
  amount: string | null;
  bank_charges: string | null;
  arrears_charges: string | null;
  status: "success" | "failed" | string;
  created_at: string;
}

export interface DashboardStats {
  users: {
    total: number;
    sdo: number;
    office_staff: number;
    meter_reader: number;
    consumer: number;
  };
  consumers: {
    total: number;
    approved_count: number;
    pending_count: number;
  };
  bills: {
    total: number;
    paid_count: number;
    unpaid_count: number;
    total_collected: string | null;
  };
  payments: {
    total_success: number;
    total_amount: string | null;
  };
}

export interface PaymentInitiate {
  mode: string;
  gateway_url: string;
  bill_id: number;
  bill_amount: string;
  amount_paisa: number;
  gateway_payload: Record<string, string | number>;
  mock_callback_hint: {
    endpoint: string;
    body: Record<string, string | number>;
  };
}

export interface PaymentResult {
  status: "success" | "failed";
  payment_id: number;
  bill_id: number;
  detail: string;
}

export interface OfficeStaffProfile {
  email: string;
  first_name: string | null;
  last_name: string | null;
  office_location: string | null;
  joining_date: string | null;
}
