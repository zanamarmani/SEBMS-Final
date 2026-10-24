New meters start from zero. Later readings use the previous accepted cumulative reading. Firebase imports sort each meter's batch by date, advance the baseline after each accepted item, and reject decreasing or backdated values. Duplicate meter/date pairs remain skipped.

Consumption is new reading minus previous reading. Monthly consumption is grouped by meter and reading calendar month before applying configured tariff slabs: first 100 units at price_100, next 100 at price_200, next 100 at price_300, remaining units at price_above. Late amount adds 10%; rounding uses Decimal to two places. Due date is 15 days after bill generation.

Manual bill generation completes directly without Celery/Redis and returns counts. Subsequent readings extend an existing unpaid bill for the same month and recalculate slabs over total units. Paid bills and ambiguous legacy multiple bills in a month are skipped for manual review; the pending readings are retained. Concurrent imports and bill generation lock meters in ID order inside a transaction.

Migration 0010 resets only the first unprocessed reading with the legacy 500 baseline where the meter has no bill. Processed readings and any meter with a bill remain unchanged. Backdated insertions require review rather than silently rewriting later consumption.
