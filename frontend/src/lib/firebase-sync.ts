export type FirebaseSyncResult = {
  status: string;
  fetched: number;
  created: number;
  skipped: number;
  invalid: number;
};

export function firebaseSyncMessage(result: FirebaseSyncResult): string {
  return `Firebase sync complete: ${result.created} imported, ${result.skipped} already present, ${result.invalid} invalid or unregistered meters (${result.fetched} fetched).`;
}
