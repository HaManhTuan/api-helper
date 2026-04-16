# Logical data model — Hanoi House Cleaning Booking API

**Source**: [`spec.md`](spec.md) + module specs under `specs/{admin,customer,helper}/`.

## Core identity

| Entity | Purpose | Key fields / notes |
|--------|---------|---------------------|
| **User** | Login identity + role | `id`, role (`customer` / `helper` / `staff` / `admin`), identifier (email/phone), `status`, timestamps |
| **StaffPermission** (logical) | RBAC for internal users | Maps `staff` user → permission codes (`admin-staff-and-roles`) |

## Customer & geography

| Entity | Purpose | Key fields / notes |
|--------|---------|---------------------|
| **SavedAddress** | Optional shortcuts | Customer-scoped; Hanoi validation |
| **Quote** | Pre-booking price bind | `id` (**`quote_id`**), `customer_id`, inputs snapshot, `expires_at` (**default +15 min** from creation), breakdown, `created_at` (**FR-043**) |

## Booking & fulfillment

| Entity | Purpose | Key fields / notes |
|--------|---------|---------------------|
| **Booking** | Core unit of work | `customer_id`, optional `helper_id`, **`quote_id`** (immutable FK), schedule, address (Hanoi), line items / `service_type`, `status`, cancellation metadata, financial snapshot when completed |
| **AvailabilitySlot** | Helper schedule | Recurrence or date + windows |
| **Review** | Post-completion | One per booking; moderation flags |

## Commercial & risk (admin-driven)

| Entity | Purpose |
|--------|---------|
| **ServiceOffering**, **PriceBook**, **CommissionRule**, **Promotion** | Catalog & pricing |
| **InsuranceProduct**, **Enrollment**, **Claim** | Risk (admin-insurance) |
| **Dispute**, **DisputeAdjustment** | Ops adjustments |
| **PayoutBatch**, **PayoutLine** | Settlement |

## Helper compliance

| Entity | Purpose | Key fields / notes |
|--------|---------|---------------------|
| **HelperDocument** | KYC | `storage_ref`, `mime` (allowed set FR-044), `status` (pending_review / …), link to helper |
| **HelperProfile** | Marketplace | Skills, service area, approval, aggregates |

## Compliance & content

| Entity | Purpose |
|--------|---------|
| **PrivacyRequest** | Customer DSAR |
| **PolicyContent** (versioned) | Terms, FAQ (`admin-content-and-policy`) |
| **AdminAuditLog** | FR-018 — actor `sub` (Staff/Admin), action, entity refs, metadata, timestamp |

## Relationships (high level)

- **Customer** 1—* **Quote**; **Quote** 0..1 used by **Booking** (first create).
- **Booking** *—1 **Customer**, *—0..1 **Helper**, *—1 **Quote** at creation.
- **Helper** 1—* **HelperDocument**, 1—* **AvailabilitySlot**.

## State machines

- **Booking**: `pending` → `accepted` → `in-progress` → `completed` | `cancelled` (+ reassignment paths) — single source: parent `spec.md` Status model.
