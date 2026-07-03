# Fichados — Task Board

> Each task is scoped to be a single Pull Request (~1 day of full work).
> Tasks follow the project's screaming architecture with vertical slicing.
> Dependencies are explicit — a task cannot start until its blockers are merged.

## Conventions

- **Branch naming**: `feat/<task-id>-short-description` (e.g., `feat/T01-project-bootstrap`)
- **PR scope**: One task = one PR. No mixing concerns.
- **Architecture**: Each module lives in `src/modules/<module>/` with layers: `domain/`, `application/`, `infrastructure/`.
- **Tests mirror source**: `test/modules/<module>/` mirrors `src/modules/<module>/`.
- **Commits**: Conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).

---

## Phase 0 — Foundation

### T01: Project Bootstrap & Configuration: Done

**Blocked by:** Nothing
**PR scope:** Project setup, tooling, and shared infrastructure.

- [x] Initialize Python project with `pyproject.toml` (dependencies, scripts, linting)
- [x] Configure linter (ruff) and formatter
- [x] Configure test runner (pytest)
- [x] Create `src/shared/` directory for cross-module concerns (value objects, base classes, exceptions)
- [x] Define base entity class (`src/shared/domain/entity.py`)
- [x] Define base value object class (`src/shared/domain/value_object.py`)
- [x] Define shared custom exceptions (`src/shared/domain/exceptions.py`)
- [x] Define repository interface contract (`src/shared/domain/repository.py`)
- [x] Verify the test pipeline runs: `pytest` passes with at least one smoke test
- [x] Update `.gitignore` with Python defaults

**Deliverable:** A clean, runnable project skeleton with shared domain building blocks.

---

## Phase 1 — Core Domain Entities (Inside-Out)

### T02: Player Module — Domain Layer

**Blocked by:** T01
**PR scope:** Complete Player entity with value objects and domain rules.

- [ ] Define `Player` entity with all fields from spec (id, name, age, score, location, position, photoId, cityId, email, phoneNumber)
- [ ] Create value objects: `PlayerId`, `Email`, `PhoneNumber`, `PlayerPosition`, `PlayerScore`
- [ ] Implement validation rules (email format, age range, score bounds)
- [ ] Define `PlayerRepository` interface (abstract class)
- [ ] Unit tests for entity creation, validation, and edge cases

**Deliverable:** A fully validated Player domain model that enforces business rules at construction.

### T03: Location Module — Domain Layer (City + Field)

**Blocked by:** T01
**PR scope:** City and Field entities with value objects.

- [ ] Define `City` entity (id, name, postalCode)
- [ ] Define `Field` entity (id, location, photos, phoneNumber, name, address, cityId)
- [ ] Create value objects: `CityId`, `FieldId`, `PostalCode`, `Address`
- [ ] Define `CityRepository` and `FieldRepository` interfaces
- [ ] Unit tests for entity creation and validation

**Deliverable:** Location domain models ready to be referenced by Match and Player.

### T04: Photo Module — Domain Layer

**Blocked by:** T01
**PR scope:** Photo entity and value objects.

- [ ] Define `Photo` entity (id, url, altText)
- [ ] Create value objects: `PhotoId`, `ImageUrl`
- [ ] Define `PhotoRepository` interface
- [ ] Unit tests for entity creation and URL validation

**Deliverable:** Photo domain model ready to be referenced by Player and Field.

---

## Phase 2 — Match Domain & Lifecycle

### T05: Match Module — Domain Entity & Status Machine

**Blocked by:** T02, T03
**PR scope:** Match entity with full lifecycle state machine.

- [ ] Define `Match` entity with all fields from spec
- [ ] Create value objects: `MatchId`, `MatchStatus`, `PlayerCount`
- [ ] Implement state machine: `OPEN → CONFIRMED → COLLECTING_PAYMENTS → IN_PROGRESS → COMPLETED`
- [ ] Implement branch transitions: `CANCELLED`, `POSTPONED → OPEN`
- [ ] Enforce transition rules (e.g., can't cancel after COLLECTING_PAYMENTS)
- [ ] Implement `minQuantityPlayers` / `maxQuantityPlayers` validation
- [ ] Define `MatchRepository` interface
- [ ] Unit tests for every valid and invalid state transition
- [ ] Unit tests for player count boundary conditions

**Deliverable:** A Match entity that is impossible to put into an invalid lifecycle state.

### T06: Team Module — Domain Layer

**Blocked by:** T05
**PR scope:** Team entity supporting registered and guest players.

- [ ] Define `Team` entity (id, name, players[], guestPlayers[], numPlayers)
- [ ] Create value objects: `TeamId`
- [ ] Implement player capacity rules relative to Match constraints
- [ ] Define `TeamRepository` interface
- [ ] Unit tests for team composition and capacity limits

**Deliverable:** Team domain model that manages both registered and guest player lists.

### T07: GuestPlayer Module — Domain Layer

**Blocked by:** T05
**PR scope:** Guest player entity with invitation rules.

- [ ] Define `GuestPlayer` entity (id, name, invitedById, matchId, phoneNumber, status)
- [ ] Create value objects: `GuestPlayerId`, `GuestStatus` (INVITED, CONFIRMED, NO_SHOW)
- [ ] Implement rule: guest counts toward `currentQuantityPlayers`
- [ ] Implement rule: guest is linked to inviter (financially responsible)
- [ ] Define `GuestPlayerRepository` interface
- [ ] Unit tests for status transitions and invitation rules

**Deliverable:** GuestPlayer domain model with clear ownership and status rules.

---

## Phase 3 — Payment Domain

### T08: MatchFinancials — Domain Layer

**Blocked by:** T05
**PR scope:** Financial calculation engine for a match.

- [ ] Define `MatchFinancials` entity (id, matchId, totalFieldCost, depositAmount, costPerPlayer, reimbursementToOrganizer, fieldPaymentInfo, organizerPaymentInfo, status)
- [ ] Create value objects: `Money`, `PaymentInfo`, `FinancialStatus`
- [ ] Implement cost calculation: `costPerPlayer = totalFieldCost / totalPlayers`
- [ ] Implement reimbursement calculation: `depositAmount - costPerPlayer`
- [ ] Implement recalculation when player count changes (player joins/leaves, guest added)
- [ ] Define `MatchFinancialsRepository` interface
- [ ] Unit tests for calculation accuracy, rounding, edge cases (1 player, all guests, etc.)

**Deliverable:** A financial engine that auto-calculates costs and handles recalculations.

### T09: PlayerPayment — Domain Layer

**Blocked by:** T08, T07
**PR scope:** Individual payment records with status flow and recipient routing.

- [ ] Define `PlayerPayment` entity (id, matchId, payerId, responsiblePlayerId, guestPlayerId, amount, recipientType, paymentMethod, proofImage, status, verifiedById, verifiedAt)
- [ ] Create enums/value objects: `RecipientType` (FIELD, ORGANIZER), `PaymentMethod` (NEQUI, BANCOLOMBIA, DAVIPLATA, CASH, OTHER), `PaymentStatus` (PENDING, PROOF_SUBMITTED, VERIFIED, REJECTED)
- [ ] Implement status flow: `PENDING → PROOF_SUBMITTED → VERIFIED` and `REJECTED → PROOF_SUBMITTED`
- [ ] Implement cash-specific flow: `PENDING → VERIFIED` (receiver confirms directly)
- [ ] Implement guest payment responsibility: inviter gets multiple payments
- [ ] Define `PlayerPaymentRepository` interface
- [ ] Unit tests for status transitions, guest payment generation, recipient assignment

**Deliverable:** Payment domain model supporting digital + cash methods with proof verification.

---

## Phase 4 — Application Layer (Use Cases)

### T10: Match Use Cases — Create, Join, Confirm

**Blocked by:** T05, T06, T07
**PR scope:** Core match orchestration use cases.

- [ ] `CreateMatchUseCase`: organizer creates a match → status OPEN
- [ ] `JoinMatchUseCase`: player sends join request → organizer accepts/rejects
- [ ] `ConfirmMatchUseCase`: organizer confirms → status CONFIRMED, generates PlayerPayments
- [ ] Define input/output DTOs for each use case
- [ ] Define ports (interfaces) for external dependencies
- [ ] Unit tests with in-memory repository stubs

**Deliverable:** The three core match operations wired through the application layer.

### T11: Match Use Cases — Cancel, Postpone, Complete

**Blocked by:** T10
**PR scope:** Match lifecycle terminal and branch transitions.

- [ ] `CancelMatchUseCase`: organizer cancels → validates no payments in progress → notifies all
- [ ] `PostponeMatchUseCase`: organizer postpones → sets new date → returns to OPEN
- [ ] `CompleteMatchUseCase`: match ends → enables ratings
- [ ] `CollectPaymentsUseCase`: triggered 1h before → transitions to COLLECTING_PAYMENTS
- [ ] Enforce preconditions (can't cancel after COLLECTING_PAYMENTS, etc.)
- [ ] Unit tests for each use case including error scenarios

**Deliverable:** Full match lifecycle orchestration through use cases.

### T12: Guest Player Use Cases

**Blocked by:** T07, T10
**PR scope:** Guest invitation and management.

- [ ] `InviteGuestUseCase`: registered player invites a guest → creates GuestPlayer, increments count, recalculates finances
- [ ] `ConfirmGuestUseCase`: inviter or guest confirms attendance
- [ ] `RemoveGuestUseCase`: inviter removes guest before match → decrements count, recalculates
- [ ] Unit tests for invitation flow, capacity limits, financial recalculation

**Deliverable:** Complete guest player lifecycle through the application layer.

### T13: Payment Use Cases

**Blocked by:** T09, T11
**PR scope:** Payment orchestration and verification.

- [ ] `GeneratePaymentsUseCase`: creates PlayerPayment records for all participants when match is confirmed
- [ ] `AssignPaymentRecipientsUseCase`: organizer assigns which players pay them vs the field
- [ ] `SubmitPaymentProofUseCase`: player uploads receipt screenshot
- [ ] `VerifyPaymentUseCase`: receiver confirms/rejects a payment
- [ ] `ConfirmCashPaymentUseCase`: receiver marks cash as received
- [ ] Unit tests for each flow, including guest payment consolidation

**Deliverable:** End-to-end payment flow from generation to verification.

---

## Phase 5 — Rating & Request Modules

### T14: Rating Module — Domain + Use Cases

**Blocked by:** T11
**PR scope:** Post-match player rating system.

- [ ] Define `Rating` entity (id, ratedPlayerId, raterPlayerId, score, comment, matchId)
- [ ] Create value objects: `RatingId`, `Score` (with bounds validation)
- [ ] Implement rule: can only rate after match is COMPLETED
- [ ] Implement rule: can only rate players from the same match
- [ ] Implement rule: guest players cannot be rated
- [ ] `RatePlayerUseCase`: player rates another → updates rated player's average score
- [ ] Define `RatingRepository` interface
- [ ] Unit tests for rating rules, average calculation, duplicate prevention

**Deliverable:** Complete rating module from domain through use case.

### T15: Request Module — Domain + Use Cases

**Blocked by:** T10
**PR scope:** Match join request system.

- [ ] Define `Request` entity (id, playerId, matchId, comment, teamId)
- [ ] Create value objects: `RequestId`, `RequestStatus` (PENDING, ACCEPTED, REJECTED)
- [ ] `SendRequestUseCase`: player sends join request
- [ ] `AcceptRequestUseCase`: organizer accepts → adds player to match
- [ ] `RejectRequestUseCase`: organizer rejects → notifies player
- [ ] Define `RequestRepository` interface
- [ ] Unit tests for request flow and edge cases (match full, already joined, etc.)

**Deliverable:** Complete request module from domain through use case.

---

## Phase 6 — Infrastructure & Persistence

### T16: Database Setup & Repository Implementations

**Blocked by:** T10, T13, T14, T15
**PR scope:** Persistence layer for all modules.

- [ ] Choose and configure database (PostgreSQL recommended)
- [ ] Define ORM models / migration scripts for all entities
- [ ] Implement concrete repositories for: Player, Match, Team, GuestPlayer, MatchFinancials, PlayerPayment, Rating, Request, City, Field, Photo
- [ ] Implement Notification persistence
- [ ] Integration tests with test database

**Deliverable:** All domain repositories wired to a real database.

### T17: Notification Infrastructure

**Blocked by:** T16
**PR scope:** Notification delivery system.

- [ ] Define `Notification` entity (id, recipientId, matchId, type, message, read, createdAt)
- [ ] Implement all notification types: LOW_PLAYERS, PAYMENT_REQUEST, MATCH_REMINDER, MATCH_CANCELLED, MATCH_POSTPONED, PAYMENT_VERIFIED, PAYMENT_REJECTED, PLAYER_JOINED, GUEST_ADDED, RATE_PLAYERS
- [ ] Implement notification trigger rules:
  - Periodic LOW_PLAYERS while `current < min`
  - PAYMENT_REQUEST at 1 hour before match
  - MATCH_REMINDER at 45–30 minutes before match
- [ ] `SendNotificationUseCase` and `MarkAsReadUseCase`
- [ ] Integration tests for scheduled triggers

**Deliverable:** Notification system with all types, triggers, and timing rules.

---

## Phase 7 — API Layer

### T18: REST API — Player & Auth Endpoints

**Blocked by:** T16
**PR scope:** HTTP interface for player registration and authentication.

- [ ] Choose and configure web framework (FastAPI recommended)
- [ ] `POST /players` — register
- [ ] `POST /auth/login` — authenticate
- [ ] `GET /players/:id` — get player profile
- [ ] `PUT /players/:id` — update profile
- [ ] Implement authentication middleware (JWT)
- [ ] Input validation and error response format
- [ ] API tests

**Deliverable:** Player CRUD and auth endpoints with JWT.

### T19: REST API — Match & Team Endpoints

**Blocked by:** T18
**PR scope:** HTTP interface for match lifecycle.

- [ ] `POST /matches` — create match
- [ ] `GET /matches` — list available matches (filterable by city, date, status)
- [ ] `GET /matches/:id` — match detail with players, teams, financials
- [ ] `POST /matches/:id/confirm` — organizer confirms
- [ ] `POST /matches/:id/cancel` — organizer cancels
- [ ] `POST /matches/:id/postpone` — organizer postpones
- [ ] `POST /matches/:id/teams` — create/manage teams
- [ ] API tests

**Deliverable:** Full match management API.

### T20: REST API — Payments, Guests, Ratings, Requests

**Blocked by:** T19
**PR scope:** Remaining endpoints.

- [ ] `POST /matches/:id/guests` — invite guest
- [ ] `POST /matches/:id/requests` — send join request
- [ ] `PUT /requests/:id/accept` — accept request
- [ ] `PUT /requests/:id/reject` — reject request
- [ ] `POST /matches/:id/payments/assign` — organizer assigns payment recipients
- [ ] `POST /payments/:id/proof` — upload payment proof
- [ ] `PUT /payments/:id/verify` — verify payment
- [ ] `PUT /payments/:id/reject` — reject payment
- [ ] `POST /matches/:id/ratings` — rate a player
- [ ] `GET /players/:id/ratings` — get player ratings
- [ ] `GET /notifications` — list notifications
- [ ] `PUT /notifications/:id/read` — mark as read
- [ ] API tests

**Deliverable:** Complete REST API covering all use cases.

---

## Dependency Graph

```
T01 ──────────────────────────────────────────────────────────────
 │
 ├── T02 (Player) ──┐
 ├── T03 (Location) ─┼── T05 (Match) ──┬── T06 (Team)
 └── T04 (Photo)     │                 ├── T07 (GuestPlayer) ──┐
                     │                 ├── T08 (Financials)     │
                     │                 │     └── T09 (Payment) ─┤
                     │                 │                        │
                     │                 ├── T10 (Match UCs) ─────┤
                     │                 │     ├── T11 (Lifecycle) │
                     │                 │     ├── T12 (Guest UCs)│
                     │                 │     └── T15 (Request)  │
                     │                 │                        │
                     │                 │          T13 (Pay UCs) ┘
                     │                 │          T14 (Rating)
                     │                 │
                     │                 └── T16 (Database) ──┬── T17 (Notifications)
                     │                                      └── T18 (API: Auth)
                     │                                            └── T19 (API: Match)
                     │                                                  └── T20 (API: Rest)
```

---

## Status Legend

| Symbol | Meaning     |
| ------ | ----------- |
| ⬜     | Not started |
| 🔵     | In progress |
| 🟢     | PR merged   |
| 🔴     | Blocked     |

## Current Status

| Task | Status | PR  |
| ---- | ------ | --- |
| T01  | ⬜     | —   |
| T02  | ⬜     | —   |
| T03  | ⬜     | —   |
| T04  | ⬜     | —   |
| T05  | ⬜     | —   |
| T06  | ⬜     | —   |
| T07  | ⬜     | —   |
| T08  | ⬜     | —   |
| T09  | ⬜     | —   |
| T10  | ⬜     | —   |
| T11  | ⬜     | —   |
| T12  | ⬜     | —   |
| T13  | ⬜     | —   |
| T14  | ⬜     | —   |
| T15  | ⬜     | —   |
| T16  | ⬜     | —   |
| T17  | ⬜     | —   |
| T18  | ⬜     | —   |
| T19  | ⬜     | —   |
| T20  | ⬜     | —   |
