---
name: fastapi-templates
description: FastAPI implementation templates tailored to this repository's architecture
---

# FastAPI Project Templates

Use these templates to implement features in this existing repository architecture. Do not replace the project layout with a generic starter structure.

## When to Use This Skill

- Adding new endpoints to existing domains
- Adding service methods and repository methods
- Extending request/response/internal schemas
- Building FastAPI features while preserving current architecture

## Core Concepts

### 1. Project Structure

**Repository Layout (Use This):**

```text
app/
├── controllers/               # FastAPI routers (thin HTTP layer)
├── services/                  # Business logic, based on BaseService
├── repositories/
│   ├── core/                  # Shared repository core
│   ├── concrete/              # Domain repositories, based on FullRepositoryImpl
│   └── factory.py
├── schemas/
│   ├── common/
│   └── {domain}/              # request.py, schema.py, converters.py, __init__.py
├── models/
├── middlewares/
├── config/
└── utils/
```

### 2. Dependency Injection

Use FastAPI `Depends` for request-scoped dependencies (auth/session/current user), while keeping domain logic in services.

### 3. Async Patterns

Use `async def` for endpoint/service/repository I/O paths and avoid blocking operations in request flow.

## Implementation Patterns

### Pattern 1: Controller Pattern

```python
from fastapi import APIRouter
from app.schemas.common import ResponseBuilder, SuccessResponse
from app.schemas.users import UserCreateRequest, UserResponse
from app.services.user_service import user_service

router = APIRouter()

@router.post("/", response_model=SuccessResponse[UserResponse])  # type: ignore[misc]
async def create_user(payload: UserCreateRequest) -> SuccessResponse[UserResponse]:
    user = await user_service.create_user(payload)
    return ResponseBuilder.success(message="User created", data=user)
```

### Pattern 2: Service Pattern

```python
from app.services.base_service import BaseService
from app.models.user import User
from app.repositories.concrete.user_repository import UserRepository

class UserService(BaseService[User, UserRepository]):
    def __init__(self) -> None:
        super().__init__(UserRepository())

    async def create_user(self, user_data):
        # custom validation + business logic
        return await self.create(user_data)
```

### Pattern 3: Repository Pattern

```python
from app.repositories.core import FullRepositoryImpl
from app.repositories.factory import repository_factory
from app.models.user import User

class UserRepository(FullRepositoryImpl[User]):
    def __init__(self) -> None:
        full_repo = repository_factory.create_full_repository(User)
        super().__init__(
            model=User,
            query_builder=full_repo.query_builder,
            optimistic_lock_validator=full_repo.optimistic_lock_validator,
            relationship_handler=full_repo.relationship_handler,
        )

    async def get_by_email(self, db, email: str):
        # add domain-specific query when base methods are not enough
        ...
```

### Pattern 4: Schema Split by Domain

```python
# app/schemas/users/request.py
class UserCreateRequest(BaseSchema): ...

# app/schemas/users/schema.py (internal schema)
class UserCreate(BaseSchema): ...

# app/schemas/users/converters.py
def user_create_request_to_internal(request: UserCreateRequest) -> UserCreate: ...
```

## Role Endpoint Mapping (Spec-Aligned)

Use this mapping as the default API scope reference when adding endpoints. Source of truth:

- `docs/specs/customer/README.md`
- `docs/specs/helper/README.md`
- `docs/specs/admin/README.md`
- `docs/specs/001-housemaid-booking-api/spec.md`

### Customer API Scope

- Auth and onboarding for customer account/session.
- Profile and saved addresses management.
- Quote and booking creation flow (quote first, then create booking with `quote_id`).
- Booking history/detail and cancellation under policy rules.
- Review creation (one review per completed booking).
- Read published policy/content.
- Submit and track privacy requests.

### Helper API Scope

- Auth and onboarding for helper account/session.
- Profile, service area, and availability schedule management.
- Booking offers and helper job lifecycle actions (accept/reject/status updates).
- Earnings and payout visibility (read-only helper view).
- Reviews/ratings visibility for own performance.
- KYC document upload/status tracking.
- Insurance enrollment visibility/actions as policy allows.

### Admin and Staff API Scope

- Internal auth/access with RBAC and staff permissions.
- Staff/roles management and permission matrix.
- Customer account operations and helper moderation.
- Helper KYC verification and eligibility enforcement.
- Booking operations (list/filter/assign/reassign/cancel by policy).
- Service catalog, pricing, commission, tax, promotions.
- Disputes, adjustments, payouts, and settlement export.
- Analytics and reporting export.
- Review moderation.
- Content/policy management (version + publish).
- Audit log access and privileged action traceability.

### Cross-Role Contract Reminders

- Keep role boundaries strict; no cross-role privilege leakage.
- Keep Staff/Admin JWT behavior aligned with the same issuer/base-path model as other roles.
- Return structured authorization errors (`401`/`403`) and conflict/validation responses (`409`/`422`) per spec.

## Quick Endpoint Checklist (Copy-Paste)

Use this checklist when creating a new endpoint. Copy into PR/task description and tick items.

```md
### New Endpoint Checklist

- [ ] **Spec mapping**: Endpoint mapped to one role scope (`customer` / `helper` / `admin|staff`) in `docs/specs/*/README.md`.
- [ ] **FR mapping**: Relevant FR IDs from `docs/specs/001-housemaid-booking-api/spec.md` are listed in the task/PR.
- [ ] **Controller**: Route added in `app/controllers/` with `APIRouter`, thin handler only.
- [ ] **Service**: Business logic implemented in `app/services/` (reuse `BaseService` methods first).
- [ ] **Repository**: Data access in `app/repositories/concrete/` (reuse `FullRepositoryImpl` methods first).
- [ ] **Schemas**: Request/response/internal schemas and converter updates in `app/schemas/{domain}/`.
- [ ] **Response shape**: Uses `ResponseBuilder.success()` / `ResponseBuilder.error()`.
- [ ] **Auth/RBAC**: Role and permission checks aligned with endpoint scope.
- [ ] **Error contract**: Structured errors for `401`/`403`/`404`/`409`/`422` as applicable.
- [ ] **Eligibility vs payload**: Return `403` for authenticated-but-ineligible actor; `422` for invalid payload.
- [ ] **Rate limit**: Public endpoint included in group policy (Auth/Quote/Booking or equivalent) with structured `429`.
- [ ] **Audit log**: Privileged mutations emit audit entries (FR-018).
- [ ] **Hanoi scope**: Geography and policy constraints enforced where booking/address related.
- [ ] **Quote lock** (if booking create): `quote_id` required and stale/expired behavior aligned with FR-043.
- [ ] **KYC upload lock** (if helper docs): Presigned upload, MIME allowlist, size/TTL aligned with FR-044.
- [ ] **Tests**: Add/update unit/integration tests for happy path + key error paths.
- [ ] **Quality gates**: Run `poetry run pre-commit run --all-files` and resolve issues before merge.
```

## Implementation Guardrails

- Keep API response format consistent via `ResponseBuilder`.
- Prefer middleware-level exception formatting over ad-hoc controller handling.
- Do not introduce `app/api/v1/...` template layout unless the repository is explicitly migrated to it.
- Run validation checks with `poetry run pre-commit run --all-files` after meaningful changes.
