# Test harness shapes

The same test in four forms. Use the one your tooling supports
(`docs/agents/tooling.md`, if present). Every form has the same three parts:
fixture rows for each input, the model under test, and the exact rows
expected.

The example: *a refund within 30 days nets against the original order*.

## dbt unit tests (dbt 1.8+)

```yaml
# models/marts/_unit_tests.yml
unit_tests:
  - name: refund_within_30_days_nets_against_order
    model: fct_net_revenue
    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: 1, order_date: "2026-03-01", amount: 100.00}
      - input: ref('stg_refunds')
        rows:
          - {order_id: 1, refund_date: "2026-03-20", amount: 30.00}
    expect:
      rows:
        - {order_id: 1, order_date: "2026-03-01", net_amount: 70.00}
```

Run with `dbt test --select fct_net_revenue,test_type:unit`. Only the columns
listed in `expect` are compared, so list every column the behaviour touches.

## SQLMesh tests

```yaml
# tests/test_fct_net_revenue.yaml
test_refund_within_30_days_nets_against_order:
  model: marts.fct_net_revenue
  inputs:
    staging.stg_orders:
      rows:
        - {order_id: 1, order_date: 2026-03-01, amount: 100.00}
    staging.stg_refunds:
      rows:
        - {order_id: 1, refund_date: 2026-03-20, amount: 30.00}
  outputs:
    query:
      rows:
        - {order_id: 1, order_date: 2026-03-01, net_amount: 70.00}
```

Run with `sqlmesh test`. If the model has more columns than the test lists,
add `partial: true` under `query` so only the listed columns are compared.

## Plain SQL (any engine)

Load the fixtures into a scratch schema (or a local engine such as DuckDB),
run the model's SQL against them into `actual`, put the expected rows in
`expected`, and compare both ways:

```sql
-- zero rows = pass
(SELECT * FROM expected EXCEPT SELECT * FROM actual)
UNION ALL
(SELECT * FROM actual EXCEPT SELECT * FROM expected);
```

`EXCEPT` drops duplicates, so a model that emits a row twice would still
pass. Compare row counts as well, or use `EXCEPT ALL` where your engine has
it.

## pytest (Python transforms)

```python
import pandas as pd
from pandas.testing import assert_frame_equal

from transforms.revenue import net_revenue


def test_refund_within_30_days_nets_against_order():
    orders = pd.DataFrame(
        {"order_id": [1], "order_date": ["2026-03-01"], "amount": [100.00]})
    refunds = pd.DataFrame(
        {"order_id": [1], "refund_date": ["2026-03-20"], "amount": [30.00]})

    expected = pd.DataFrame(
        {"order_id": [1], "order_date": ["2026-03-01"], "net_amount": [70.00]})

    assert_frame_equal(net_revenue(orders, refunds), expected)
```

Keep the transform a pure function of its input frames, so the test needs no
warehouse and no cluster. If it can't be tested without live
infrastructure, the logic and the I/O are tangled — pull the logic out.
