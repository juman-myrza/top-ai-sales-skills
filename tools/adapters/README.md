# Tool Adapters

Adapters are optional runtime implementations of the contracts in [`../contracts/`](../contracts/). They are kept separate from business passports and from the universal sales skills.

| Adapter | Status | Purpose |
|---|---|---|
| [`passport-lookup/`](passport-lookup/) | Implemented locally; Hermes plugin validation passed. Not connected to a live profile | Read approved, versioned passport fields from a persistent JSON store |
| Calendar, payments, CRM, handoff, messaging | Not implemented | Contracts only |

The passport adapter is deliberately file-backed and read-only during conversations. It has no product facts, no database, and no external service dependency. See its [README](passport-lookup/README.md) for storage, deployment, publish, rollback, and failure semantics.
