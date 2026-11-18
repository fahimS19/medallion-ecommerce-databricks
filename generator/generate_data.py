import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
N_BASE = 985_000
N_EXACT_DUP = 8_000
N_KEY_DUP = 7_000
TOTAL_ROWS = N_BASE + N_EXACT_DUP + N_KEY_DUP  

rng = random.Random(SEED)

CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Sports", "Beauty"]
ORDER_STATUSES = ["COMPLETED", "SHIPPED", "PROCESSING", "CANCELLED"]
COUNTRIES = ["US", "UK", "CA", "DE", "AU", "IN"]
PAYMENT_METHODS = ["CARD", "PAYPAL", "BANK_TRANSFER", "APPLE_PAY"]
CURRENCIES = ["USD", "EUR", "GBP"]
TXN_STATUSES = ["SUCCESS", "FAILED", "PENDING"]

start_date = datetime(2026, 1, 1)


def rand_date_str():
    d = start_date + timedelta(days=rng.randint(0, 300))
    return d.strftime("%Y-%m-%d")


def rand_ts_str(base_date_str):
    base = datetime.strptime(base_date_str, "%Y-%m-%d")
    ts = base + timedelta(
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
        seconds=rng.randint(0, 59),
    )
    return ts.strftime("%Y-%m-%d %H:%M:%S")


print("Generating 1,000,000 rows for orders.csv...")
orders = []
order_lookup = {}  # order_id -> (date_str, total_amount)

for i in range(1, N_BASE + 1):
    oid = f"ORD-{i:07d}"
    cid = f"CUST-{rng.randint(1, 50000):05d}"
    odate = rand_date_str()
    cat = rng.choice(CATEGORIES)
    qty = rng.randint(1, 6)
    price = round(rng.uniform(10.0, 450.0), 2)
    status = rng.choices(ORDER_STATUSES, weights=[0.72, 0.12, 0.06, 0.10])[0]
    country = rng.choice(COUNTRIES)
    orders.append([oid, cid, odate, cat, str(qty), f"{price:.2f}", status, country])
    order_lookup[oid] = (odate, round(qty * price, 2))

# Inject mutually exclusive dirty categories into orders
order_dirty_idx = rng.sample(range(N_BASE), 50_000)

for idx in order_dirty_idx[0:10_000]:  # 1. Null / blank values
    col = rng.choice([1, 3, 7])
    orders[idx][col] = ""

for idx in order_dirty_idx[10_000:18_000]:  # 2. Text in numeric fields
    if rng.random() < 0.5:
        orders[idx][4] = rng.choice(["two", "N/A", "qty_err"])
    else:
        orders[idx][5] = rng.choice(["free", "TBD", "abc"])

for idx in order_dirty_idx[18_000:26_000]:  # 3. Negative / zero numeric values
    if rng.random() < 0.5:
        orders[idx][4] = str(rng.choice([-3, -1, 0]))
    else:
        orders[idx][5] = f"{rng.choice([-49.99, -10.00, 0.00]):.2f}"

for idx in order_dirty_idx[26_000:33_000]:  # 4. Invalid / future dates
    orders[idx][2] = rng.choice(["2027-06-15", "2028-01-01", "invalid-date", "2026-13-45"])

for idx in order_dirty_idx[33_000:38_000]:  # 5. Invalid domain labels
    if rng.random() < 0.5:
        orders[idx][6] = "UNKNOWN_STATUS"
    else:
        orders[idx][7] = "ZZ"

for idx in order_dirty_idx[38_000:50_000]:  # 6. Inconsistent case / whitespace (cleanable)
    orders[idx][3] = f"  {orders[idx][3].lower()} "
    orders[idx][6] = f" {orders[idx][6].lower()}  "

# 7. Exact row duplicates & duplicate business keys
clean_order_pool = list(set(range(N_BASE)) - set(order_dirty_idx))
dup_order_samples = rng.sample(clean_order_pool, N_EXACT_DUP + N_KEY_DUP)

for idx in dup_order_samples[:N_EXACT_DUP]:
    orders.append(list(orders[idx]))

for idx in dup_order_samples[N_EXACT_DUP:]:
    row_copy = list(orders[idx])
    row_copy[4] = str(int(row_copy[4]) + 1)
    orders.append(row_copy)

rng.shuffle(orders)

with open("orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "order_id", "customer_id", "order_date", "category",
        "quantity", "unit_price", "order_status", "country"
    ])
    writer.writerows(orders)

print("Generating 1,000,000 rows for transactions.csv...")
txns = []
for i in range(1, N_BASE + 1):
    tid = f"TXN-{i:07d}"
    ref_num = rng.randint(1, N_BASE)
    oid = f"ORD-{ref_num:07d}"
    odate_str, total_amt = order_lookup[oid]
    pm = rng.choice(PAYMENT_METHODS)
    curr = rng.choices(CURRENCIES, weights=[0.75, 0.15, 0.10])[0]
    tstatus = rng.choices(TXN_STATUSES, weights=[0.85, 0.10, 0.05])[0]
    tts = rand_ts_str(odate_str)
    txns.append([tid, oid, pm, f"{total_amt:.2f}", curr, tstatus, tts])

txn_dirty_idx = rng.sample(range(N_BASE), 59_000)

for k, idx in enumerate(txn_dirty_idx[0:12_000]):  # 1. Orphan order_id
    txns[idx][1] = f"ORD-{9000001 + k:07d}"

for idx in txn_dirty_idx[12_000:21_000]:  # 2. Null / blank values
    col = rng.choice([2, 3, 6])
    txns[idx][col] = ""

for idx in txn_dirty_idx[21_000:28_000]:  # 3. Text in numeric amount
    txns[idx][3] = rng.choice(["N/A", "ERR_AMT", "pending"])

for idx in txn_dirty_idx[28_000:35_000]:  # 4. Negative / out-of-range amount
    txns[idx][3] = f"{rng.choice([-25.00, -100.50, 0.00, 9999999.99]):.2f}"

for idx in txn_dirty_idx[35_000:42_000]:  # 5. Invalid / future timestamps
    txns[idx][6] = rng.choice(["2027-09-10 14:22:00", "2028-03-01 00:00:00", "bad-timestamp"])

for idx in txn_dirty_idx[42_000:47_000]:  # 6. Unsupported currency / status
    if rng.random() < 0.5:
        txns[idx][4] = "XYZ"
    else:
        txns[idx][5] = "GLITCH"

for idx in txn_dirty_idx[47_000:59_000]:  # 7. Inconsistent case / whitespace
    txns[idx][2] = f" {txns[idx][2].lower()} "
    txns[idx][4] = f" {txns[idx][4].lower()} "
    txns[idx][5] = f" {txns[idx][5].capitalize()} "

# 8. Exact row duplicates & duplicate business keys
clean_txn_pool = list(set(range(N_BASE)) - set(txn_dirty_idx))
dup_txn_samples = rng.sample(clean_txn_pool, N_EXACT_DUP + N_KEY_DUP)

for idx in dup_txn_samples[:N_EXACT_DUP]:
    txns.append(list(txns[idx]))

for idx in dup_txn_samples[N_EXACT_DUP:]:
    row_copy = list(txns[idx])
    dt = datetime.strptime(row_copy[6], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=5)
    row_copy[6] = dt.strftime("%Y-%m-%d %H:%M:%S")
    txns.append(row_copy)

rng.shuffle(txns)

with open("transactions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "txn_id", "order_id", "payment_method", "amount",
        "currency", "txn_status", "txn_ts"
    ])
    writer.writerows(txns)

orders_bytes = os.path.getsize("orders.csv")
txns_bytes = os.path.getsize("transactions.csv")

report = f"""# Synthetic Data & Dirty-Data Inventory (Seed = {SEED})

## File Inventory
| File | Volume Target Path | Data Rows (Excl. Header) | File Size (Bytes) |
| :--- | :--- | ---: | ---: |
| `orders.csv` | `/Volumes/workspace/ecom_poc/raw_files/orders.csv` | {len(orders):,} | {orders_bytes:,} |
| `transactions.csv` | `/Volumes/workspace/ecom_poc/raw_files/transactions.csv` | {len(txns):,} | {txns_bytes:,} |

## Injected Dirty-Data Breakdown — `orders.csv`
| Dirty Category | Target Field(s) | Injected Count | % of 1,000,000 |
| :--- | :--- | ---: | ---: |
| Null / blank values | `customer_id`, `category`, `country` | 10,000 | 1.00% |
| Text in numeric fields | `quantity`, `unit_price` | 8,000 | 0.80% |
| Negative / zero numeric values | `quantity`, `unit_price` | 8,000 | 0.80% |
| Invalid / future dates | `order_date` | 7,000 | 0.70% |
| Invalid domain labels | `order_status`, `country` | 5,000 | 0.50% |
| Inconsistent case / whitespace | `category`, `order_status` | 12,000 | 1.20% |
| Exact duplicate rows | All columns | 8,000 | 0.80% |
| Duplicate business keys (modified attributes) | `order_id` | 7,000 | 0.70% |

## Injected Dirty-Data Breakdown — `transactions.csv`
| Dirty Category | Target Field(s) | Injected Count | % of 1,000,000 |
| :--- | :--- | ---: | ---: |
| Orphan order references | `order_id` | 12,000 | 1.20% |
| Null / blank values | `payment_method`, `amount`, `txn_ts` | 9,000 | 0.90% |
| Text in numeric field | `amount` | 7,000 | 0.70% |
| Negative / out-of-range values | `amount` | 7,000 | 0.70% |
| Invalid / future timestamps | `txn_ts` | 7,000 | 0.70% |
| Unsupported currency / status | `currency`, `txn_status` | 5,000 | 0.50% |
| Inconsistent case / whitespace | `payment_method`, `currency`, `txn_status` | 12,000 | 1.20% |
| Exact duplicate rows | All columns | 8,000 | 0.80% |
| Duplicate business keys (later timestamp) | `txn_id` | 7,000 | 0.70% |
"""

with open("generator/dirty_data_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Done! Created orders.csv, transactions.csv, and generator/dirty_data_report.md")