# Product Pulse architecture

```text
Public datasets
      |
      v
clean_data.py
      |
      v
cleaned Parquet
      |
      +--------------------+
      |                    |
      v                    v
build_features.py      experiment analytics
      |                    |
      v                    |
modeling Parquet           |
      |                    |
      +--------+-----------+
               |
       +-------+-------+
       |               |
       v               v
propensity         uplift T-learner
models             models
       |               |
       +-------+-------+
               |
               v
         decision policies
               |
               v
            FastAPI
               |
               v
         Next.js dashboard
```

## Separation of concerns

- **Notebooks**: research, EDA, model development, visual explanation.
- **`src/`**: reusable/testable domain logic.
- **`scripts/`**: orchestration and repeatable batch jobs.
- **`api/`**: serving compact analytics/model/decision outputs.
- **`dashboard/`**: product-facing presentation layer.
- **`results/`**: immutable compact outputs used by the demo API.
- **`artifacts/`**: generated model bundles, excluded from Git.

The four public datasets are independent and are never joined as if they represented a single user population.
