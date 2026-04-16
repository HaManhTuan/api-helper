# REST contracts — summary

**Binding rules**: Parent [`spec.md`](../spec.md) **FR-043**, **FR-044**, **FR-045**. Detailed module behavior remains in `specs/{admin,customer,helper}/`.

## Authentication

- **Header**: `Authorization: Bearer <access_token>`
- **JWT**: Single issuer for **Customer**, **Helper**, **Staff**, **Admin** (FR-045).
- **Claims**: `sub`; `roles`; `permissions` (required for Staff; Admin = full access).

## Quote & booking (FR-043)

| Method | Path (illustrative) | Auth | Notes |
|--------|---------------------|------|--------|
| `POST` | `/quotes` | Customer | Returns **`quote_id`**, breakdown, **`expires_at`** (~15 min) |
| `POST` | `/bookings` | Customer | Body **must** include **`quote_id`**; 422/409 if invalid/expired/stale |

## Helper KYC upload (FR-044)

| Step | Notes |
|------|--------|
| Request presigned URL | Server validates document type; returns PUT URL + required `Content-Type` |
| Client `PUT` | Allowlist MIME: `image/jpeg`, `image/png`, `application/pdf`; max **10 MiB**; URL TTL **15 min** |

## Error shape

- **FR-023 / FR-024**: Structured errors (codes + fields + human-readable messages) for validation, auth, not-found, conflict.

## Further detail

- OpenAPI / JSON Schema files MAY be added in this folder in a later iteration when implementation stabilizes path names and DTOs.
