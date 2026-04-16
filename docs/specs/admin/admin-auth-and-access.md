# Feature Specification: Admin — Authentication & Access Control

**See also**: [`admin-staff-and-roles.md`](admin-staff-and-roles.md) for **multiple** staff accounts and **permission matrix** (this file focuses on **session** and **authentication** mechanics).

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Parent feature admin cluster: secure Admin access, JWT + RBAC, internal-only Admin accounts (no public self-registration).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin signs in to the dashboard API (Priority: P1)

An operations user with an **Admin** role uses issued credentials to obtain a **JWT** and calls protected admin-only endpoints. Non-admin tokens cannot perform admin actions.

**Why this priority**: Without authenticated Admin access, no other admin cluster is usable.

**Independent Test**: Provision an Admin user (out-of-band or internal endpoint per planning), login, call a protected admin route with token → 200; same route with Customer token → 403.

**Acceptance Scenarios**:

1. **Given** valid Admin credentials, **When** the client requests login, **Then** the response includes a JWT whose claims identify the user as **Admin** (or equivalent server-side role binding).
2. **Given** a valid Admin JWT, **When** the client calls an admin-only endpoint, **Then** the request succeeds when authorized.
3. **Given** a Customer or Helper JWT, **When** the client calls an admin-only endpoint, **Then** the system returns **403** with a structured error (no data leak).

---

### User Story 2 - Admin accounts cannot self-register publicly (Priority: P1)

The public registration API accepts **Customer** and **Helper** only. **Admin** accounts are created through **internal** processes (manual provisioning, seed, or internal tool—not exposed as open signup).

**Why this priority**: Prevents privilege escalation via public signup.

**Independent Test**: Attempt `POST /register` (or equivalent) with `role=admin` from public client → rejected; Admin exists only via internal creation path.

**Acceptance Scenarios**:

1. **Given** a public registration request specifying Admin role, **When** it is submitted, **Then** the system rejects it with a clear error (or ignores role and does not create Admin).
2. **Given** an internal provisioning flow (documented in planning), **When** an Admin record is created, **Then** that user can authenticate as Admin per US1.

---

### User Story 3 - Session refresh and sign-out behavior (Priority: P2)

Admins can refresh tokens (if refresh tokens are used) and invalidate sessions on sign-out where the product supports it, without weakening RBAC checks on the server.

**Why this priority**: Operational security and predictable session lifetime.

**Independent Test**: Login → refresh (if applicable) → logout/revoke → subsequent API calls with old token fail.

**Acceptance Scenarios**:

1. **Given** refresh is enabled in planning, **When** Admin submits a valid refresh request, **Then** a new access token is issued per policy.
2. **Given** sign-out invalidates tokens server-side (if implemented), **When** a revoked token is used, **Then** requests are rejected with **401**.

---

### Edge Cases

- **Stolen token**: Short-lived access tokens + server-side role checks; optional token blocklist for Admin on suspend.
- **Role change while token valid**: Server MUST enforce current role/permissions from source of truth, not only JWT claims, for sensitive admin actions (or document token invalidation on role change).
- **Brute force**: Login rate limiting and lockout policy (detail in planning).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-AUTH-001**: System MUST authenticate Admin users and issue **JWT** access tokens consistent with the parent feature.
- **ADM-AUTH-002**: System MUST enforce **RBAC** so Admin routes are inaccessible to Customer and Helper roles.
- **ADM-AUTH-003**: System MUST NOT allow **public self-registration** for Admin role.
- **ADM-AUTH-004**: System MUST document **internal** Admin provisioning (seed, admin-only tool, or break-glass process) in planning.
- **ADM-AUTH-005**: System MUST return **structured errors** for **401** (unauthenticated) and **403** (forbidden) on admin routes.

### Key Entities *(include if feature involves data)*

- **User (Admin)**: Same core user entity as parent feature; `role = admin`, `status` active/suspended.
- **Session / token metadata** (if stored): Optional refresh token id, expiry, revocation flag—exact shape in planning.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-A1**: **100%** of sampled admin-only endpoints in a test matrix reject non-Admin tokens with **403** (or **401** when unauthenticated).
- **SC-A2**: **0** successful public registrations resulting in Admin role in security test suite.

## Assumptions

- Password or credential policy for internal Admins follows organization defaults defined in planning.
- **MFA** (TOTP/WebAuthn): **SHOULD** bật bắt buộc cho **Super Admin** và role **payouts:approve**; **MAY** mở rộng toàn staff theo chính sách tổ chức.
