export type BillGenerationResult = {
  status: string;
  processed: number;
  bills_created: number;
  bills_updated: number;
  skipped: number;
};

export function billGenerationMessage(result: BillGenerationResult): string {
  return `Billing complete: ${result.bills_created} created, ${result.bills_updated} updated, ${result.processed} readings processed, ${result.skipped} skipped.`;
}
