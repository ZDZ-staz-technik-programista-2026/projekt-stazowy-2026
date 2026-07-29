# Known Issues & Technical Debt

## Overview
This document tracks known limitations, resolved defects, and deferred technical debt across project quality gates (KAN-55, KAN-56, KAN-61).

---

## Resolved High-Priority Issues

### 1. KI-1: Daily and Weekly Worked-Hours Limits Bypass via PATCH
- **Priority:** High
- **Status:** Resolved (PR #58 / KAN-56)
- **Resolution:** Updated `PATCH` endpoint logic to strictly enforce daily and weekly worked-hours validation via `check_hours_limit(..., exclude_entry_id=entry.id)`. Verified with backend regression tests.

### 2. KI-2: Unhandled Server Error on Timezone-Aware Time Input
- **Priority:** High
- **Status:** Resolved (PR #59 / KAN-56)
- **Resolution:** Added strict validation in request models to reject timezone-aware datetime values, returning `400 INVALID_FIELD_FORMAT` instead of an unhandled 500 error. Verified with backend regression tests.

---

## Cross-Module Review Findings (KAN-61)

### 1. Backend Business Logic
- **Primary Owner:** Michał Misiewicz | **Reviewer:** Jakub Lewkowicz (Kuba)
- **Status:** No findings. Business logic, validation rules, and status transitions met requirements.

### 2. Frontend Application
- **Primary Owner:** Jakub Lewkowicz (Kuba) | **Reviewer:** Kacper Musiaka
- **Status:** No findings. Dashboard, forms, routing, and API integration working correctly.

### 3. Approval Queue, REST Endpoints & Database Integration
- **Primary Owner:** Kacper Musiaka | **Reviewer:** Michał Misiewicz
- **Status:** No findings. Endpoint behavior, CRUD operations, and database consistency verified.

---

## Deferred Limitations & Technical Debt

### 1. KI-3: Direct Database / Import Limit Bypass Risk
- **Priority:** Medium
- **Status:** Mitigated / Deferred (from KAN-55)
- **Impact:** Direct DB modifications or bulk imports could bypass application-level worked-hours limits.
- **Deferral Rationale:** The API is currently the sole write path in the MVP. All API endpoints enforce limits. To be revisited if seeders or CSV imports are introduced.

### 2. KI-4: Unaggregated Validation Error Messages
- **Priority:** Low
- **Status:** Open / Deferred (from KAN-55)
- **Impact:** Multiple validation failures return separate error messages rather than a single aggregated structure.
- **Deferral Rationale:** Does not block core execution or data integrity. Non-blocking UX enhancement deferred past current MVP.