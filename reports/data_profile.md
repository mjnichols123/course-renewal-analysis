# Course Renewal Dataset Profile

This report was generated automatically from the cleaned tables.

## Dataset overview

| table | rows | columns | duplicate_rows |
| --- | --- | --- | --- |
| email_blasts.parquet | 619186 | 6 | 0 |
| expirations.parquet | 127928 | 4 | 3983 |
| orders.parquet | 38524 | 3 | 8172 |

## Relationships between tables

| left_table | right_table | left_unique_ids | right_unique_ids | shared_ids | left_overlap_pct | right_overlap_pct |
| --- | --- | --- | --- | --- | --- | --- |
| email_blasts.parquet | expirations.parquet | 100000 | 76875 | 76875 | 76.88% | 100.00% |
| email_blasts.parquet | orders.parquet | 100000 | 18537 | 18537 | 18.54% | 100.00% |
| expirations.parquet | orders.parquet | 76875 | 18537 | 16299 | 21.20% | 87.93% |

### Working entity relationship model

```text
email_blinded_index
        │
        ├── email_blasts
        ├── expirations
        └── orders
```

## email_blasts.parquet

Each row represents one blinded email recipient included in an email blast sent on a particular date.

### Table summary

- Rows: 619,186
- Columns: 6
- Fully duplicated rows: 0
- Duplicate-row percentage: 0.00%

### Column profile

| column | dtype | role | missing | missing_pct | unique | unique_pct |
| --- | --- | --- | --- | --- | --- | --- |
| sent_at | datetime64[ns] | Date/time | 0 | 0.00% | 45 | 0.01% |
| is_large_blast | int64 | Binary indicator | 0 | 0.00% | 2 | 0.00% |
| email_blinded_index | int64 | Identifier | 0 | 0.00% | 100000 | 16.15% |
| blinded_course_2_exp | datetime64[ns] | Date/time | 182767 | 29.52% | 5410 | 0.87% |
| blinded_course_9_exp | datetime64[ns] | Date/time | 580096 | 93.69% | 2752 | 0.44% |
| blinded_course_10_exp | datetime64[ns] | Date/time | 443853 | 71.68% | 4177 | 0.67% |

### Candidate keys

- Composite candidate: `sent_at`, `email_blinded_index`
- Composite candidate: `sent_at`, `email_blinded_index`, `is_large_blast`

### Date ranges

| column | minimum | maximum |
| --- | --- | --- |
| sent_at | 2025-03-21T00:00:00 | 2026-07-02T00:00:00 |
| blinded_course_2_exp | 2010-06-10T00:00:00 | 2093-03-31T00:00:00 |
| blinded_course_9_exp | 2014-06-27T00:00:00 | 2028-04-30T00:00:00 |
| blinded_course_10_exp | 1992-01-08T00:00:00 | 2031-10-17T00:00:00 |

### Most common values

#### `is_large_blast`

| value | count | percentage |
| --- | --- | --- |
| 0 | 412026 | 66.54% |
| 1 | 207160 | 33.46% |

### Initial business interpretation

- Unique blinded email identifiers: 100,000
- Average records per blinded email identifier: 6.19
- Unique email blast dates: 45

## expirations.parquet

Each row represents one certification-course expiration associated with a blinded email identifier.

### Table summary

- Rows: 127,928
- Columns: 4
- Fully duplicated rows: 3,983
- Duplicate-row percentage: 3.11%

### Column profile

| column | dtype | role | missing | missing_pct | unique | unique_pct |
| --- | --- | --- | --- | --- | --- | --- |
| email_blinded_index | int64 | Identifier | 0 | 0.00% | 76875 | 60.09% |
| expired_date | datetime64[ns] | Date/time | 1288 | 1.01% | 3861 | 3.02% |
| course_blinded_index | int64 | Identifier | 0 | 0.00% | 20 | 0.02% |
| our_course | int64 | Binary indicator | 0 | 0.00% | 2 | 0.00% |

### Candidate keys

No tested single-column or table-specific composite key uniquely identifies every row.

### Date ranges

| column | minimum | maximum |
| --- | --- | --- |
| expired_date | 2018-01-02T00:00:00 | 2093-03-31T00:00:00 |

### Most common values

#### `course_blinded_index`

| value | count | percentage |
| --- | --- | --- |
| 2 | 80896 | 63.24% |
| 10 | 34131 | 26.68% |
| 9 | 9207 | 7.20% |
| 11 | 1045 | 0.82% |
| 8 | 841 | 0.66% |

#### `our_course`

| value | count | percentage |
| --- | --- | --- |
| 0 | 85090 | 66.51% |
| 1 | 42838 | 33.49% |

### Initial business interpretation

- Unique blinded email identifiers: 76,875
- Average records per blinded email identifier: 1.66
- Unique blinded courses: 20

## orders.parquet

Each row represents one order associated with a blinded email identifier.

### Table summary

- Rows: 38,524
- Columns: 3
- Fully duplicated rows: 8,172
- Duplicate-row percentage: 21.21%

### Column profile

| column | dtype | role | missing | missing_pct | unique | unique_pct |
| --- | --- | --- | --- | --- | --- | --- |
| created_at | datetime64[ns] | Date/time | 0 | 0.00% | 9547 | 24.78% |
| email_blinded_index | int64 | Identifier | 0 | 0.00% | 18537 | 48.12% |
| price | float64 | Numeric | 0 | 0.00% | 615 | 1.60% |

### Candidate keys

No tested single-column or table-specific composite key uniquely identifies every row.

### Date ranges

| column | minimum | maximum |
| --- | --- | --- |
| created_at | 2020-01-01T16:00:00 | 2026-07-09T01:47:25 |

### Most common values

### Initial business interpretation

- Unique blinded email identifiers: 18,537
- Average records per blinded email identifier: 2.08
- Total recorded revenue: $7,620,435.85
- Median order price: $175.00
