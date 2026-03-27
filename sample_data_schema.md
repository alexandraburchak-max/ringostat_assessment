# Sample Data Schema

The dashboard supports a canonical schema and also maps common aliases from CRM exports.

| Canonical column | Type | Description | Example | Accepted aliases |
|---|---|---|---|---|
| `deal_id` | string / int | Unique deal identifier | `D-10234` | `deal_id`, `id` |
| `created_date` | date | Deal creation date | `2024-04-03` | `created_date`, `created_at`, `AQL date` |
| `closing_date` | date | Deal close date for won/lost deals | `2024-04-20` | `closing_date`, `close_date`, `Closing Date` |
| `client_country` | string | Client country | `UA (Ukraine)` | `client_country`, `country`, `Client country` |
| `client_crm` | string | CRM used by client | `Bitrix24` | `client_crm`, `crm`, `Client CRM` |
| `source` | string | Lead acquisition source | `Partner` | `source`, `Source` |
| `stage` | string | Pipeline stage | `Closed Won` | `stage`, `Stage` |
| `ppc_budget` | string / numeric | PPC budget amount or range in USD | `500-1000`, `0`, `1200` | `ppc_budget`, `ppc_budget_usd`, `PPC budget USD` |

## Stage values

Expected stage values include at minimum:
- `Closed Won`
- `Closed Lost`

Additional open stages are supported and shown in distribution charts.
