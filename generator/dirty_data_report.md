# Synthetic Data & Dirty-Data Inventory (Seed = 42)

## File Inventory
| File | Volume Target Path | Data Rows (Excl. Header) | File Size (Bytes) |
| :--- | :--- | ---: | ---: |
| `orders.csv` | `/Volumes/workspace/ecom_poc/raw_files/orders.csv` | 1,000,000 | 65,808,369 |
| `transactions.csv` | `/Volumes/workspace/ecom_poc/raw_files/transactions.csv` | 1,000,000 | 73,105,132 |

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
