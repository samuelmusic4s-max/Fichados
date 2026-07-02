# Fichados — Product Specification

> Football match coordination platform connecting players, organizers, and fields.

---

## Table of Contents

1. [Glossary](#glossary)
2. [Entity Model](#entity-model)
3. [Match Lifecycle](#match-lifecycle)
4. [Payment System](#payment-system)
5. [Guest Player System](#guest-player-system)
6. [Notification System](#notification-system)
7. [Rating System](#rating-system)
8. [Use Cases](#use-cases)

---

## Glossary

| Term | Definition |
| --- | --- |
| Organizer | The player who creates and manages a match |
| Guest Player | A non-registered person invited to a match by a registered player |
| Inviter | The registered player who invited a guest player and is financially responsible for them |
| Deposit | The upfront payment the organizer makes to reserve the field |
| Reimbursement | The amount other players owe the organizer to cover the deposit minus their own share |
| Recipient | The entity that receives a payment (either the field or the organizer) |

---

## Entity Model

### Player

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| name | string | Full name |
| age | number | Player's age |
| score | number | Average rating from other players |
| location | string | General location |
| position | string | Preferred playing position |
| photoId | UUID | Reference to profile photo |
| cityId | UUID | Reference to city |
| password | string | Hashed password |
| email | string | Unique email address |
| phoneNumber | string | Contact number |

### Match

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| teams | UUID[] | References to teams |
| currentQuantityPlayers | number | Players currently joined (includes guests) |
| maxQuantityPlayers | number | Maximum capacity |
| minQuantityPlayers | number | Minimum threshold for notifications |
| fieldId | UUID | Reference to the field |
| price | number | Total field cost (varies by schedule, entered manually) |
| time | string | Start time |
| date | date | Match date |
| organizerId | UUID | Player who created and manages the match |
| cityId | UUID | Reference to city |
| location | string | Match location details |
| status | enum | Current lifecycle state (see [Match Lifecycle](#match-lifecycle)) |
| createdAt | timestamp | Creation timestamp |

### Team

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| name | string | Team name |
| players | UUID[] | Registered player references |
| guestPlayers | UUID[] | Guest player references |
| numPlayers | number | Total player count |

### GuestPlayer

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| name | string | Name provided by the inviter |
| invitedById | UUID | Player who invited them (financially responsible) |
| matchId | UUID | Match they were invited to |
| phoneNumber | string? | Optional, for sending invitation links |
| status | enum | `INVITED` · `CONFIRMED` · `NO_SHOW` |

### Request

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| playerId | UUID | Player requesting to join |
| matchId | UUID | Target match |
| comment | string | Optional message to the organizer |
| teamId | UUID | Preferred team |

### MatchFinancials

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| matchId | UUID | Reference to match |
| totalFieldCost | number | Total field rental cost |
| depositAmount | number | Amount the organizer paid to reserve |
| depositPaidById | UUID | Player who paid the deposit (organizer) |
| costPerPlayer | number | Calculated: `totalFieldCost / totalPlayers` |
| reimbursementToOrganizer | number | Calculated: `depositAmount - costPerPlayer` |
| fieldPaymentInfo | string | Payment details for the field (Nequi, bank account, etc.) |
| organizerPaymentInfo | string | Organizer's payment details for reimbursement |
| status | enum | `PENDING` · `COLLECTING` · `COMPLETED` |

### PlayerPayment

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| matchId | UUID | Reference to match |
| payerId | UUID | Player responsible for this payment |
| responsiblePlayerId | UUID? | If paying for a guest, points to the inviter |
| guestPlayerId | UUID? | Reference to the guest player (if applicable) |
| amount | number | Amount to pay |
| recipientType | enum | `FIELD` · `ORGANIZER` |
| paymentMethod | enum | `NEQUI` · `BANCOLOMBIA` · `DAVIPLATA` · `CASH` · `OTHER` |
| proofImage | string? | URL of payment receipt screenshot |
| status | enum | `PENDING` · `PROOF_SUBMITTED` · `VERIFIED` · `REJECTED` |
| verifiedById | UUID? | Who verified the payment |
| verifiedAt | timestamp? | When it was verified |

### Field

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| location | string | GPS coordinates or location reference |
| photos | UUID[] | Reference to field photos |
| phoneNumber | string | Contact number |
| name | string | Field name |
| address | string | Physical address |
| cityId | UUID | Reference to city |

### City

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| name | string | City name |
| postalCode | string | Postal code |

### Rating

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| ratedPlayerId | UUID | Player being rated |
| raterPlayerId | UUID | Player giving the rating |
| score | number | Numeric score |
| comment | string? | Optional feedback |
| matchId | UUID | Match context for the rating |

### Photo

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| url | string | Image URL |
| altText | string | Accessible description |

### Notification

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Unique identifier |
| recipientId | UUID | Player receiving the notification |
| matchId | UUID | Related match |
| type | enum | See [Notification Types](#notification-types) |
| message | string | Notification content |
| read | boolean | Whether it has been read |
| createdAt | timestamp | When it was created |

---

## Match Lifecycle

### State Machine

```
OPEN ──→ CONFIRMED ──→ COLLECTING_PAYMENTS ──→ IN_PROGRESS ──→ COMPLETED
  │          │
  ▼          ▼
CANCELLED  POSTPONED ──→ OPEN (rescheduled with new date/time)
```

### States

| State | Description | Transitions To |
| --- | --- | --- |
| `OPEN` | Visible and accepting players | `CONFIRMED`, `CANCELLED`, `POSTPONED` |
| `CONFIRMED` | Organizer confirmed the match will happen | `COLLECTING_PAYMENTS`, `CANCELLED`, `POSTPONED` |
| `COLLECTING_PAYMENTS` | 1 hour before match. Players are notified to pay | `IN_PROGRESS` |
| `IN_PROGRESS` | Match is being played | `COMPLETED` |
| `COMPLETED` | Match finished. Rating system enabled | — (terminal) |
| `CANCELLED` | Organizer cancelled. Only before `COLLECTING_PAYMENTS` | — (terminal) |
| `POSTPONED` | Organizer postponed. Returns to `OPEN` with new date | `OPEN` |

### Rules

- **Cancellation and postponement** can only happen BEFORE `COLLECTING_PAYMENTS`. No money is at risk at that point.
- When postponed, a new date/time is set and the match returns to `OPEN`.
- `currentQuantityPlayers` includes both registered players and guest players.

---

## Payment System

### Cost Calculation

All players (registered and guests) pay the same fixed amount:

```
costPerPlayer = totalFieldCost / totalPlayers
reimbursementToOrganizer = depositAmount - costPerPlayer
```

**Example:**

```
Field cost:     100,000 COP
Deposit:         30,000 COP (paid by organizer to reserve)
Players:              10
Cost per player: 10,000 COP
Organizer overpaid: 30,000 - 10,000 = 20,000 COP → 2 players reimburse organizer
```

### Payment Recipients

Each `PlayerPayment` has one of two recipient types:

| Recipient | Description |
| --- | --- |
| `FIELD` | Payment goes directly to the field's account |
| `ORGANIZER` | Payment goes to the organizer to reimburse their deposit |

The **organizer manually assigns** which players pay them (to cover the deposit reimbursement). All remaining players pay the field directly.

### Payment Methods

| Method | Verification |
| --- | --- |
| `NEQUI` | Player uploads receipt screenshot → receptor verifies |
| `BANCOLOMBIA` | Player uploads receipt screenshot → receptor verifies |
| `DAVIPLATA` | Player uploads receipt screenshot → receptor verifies |
| `CASH` | Receptor manually confirms receipt in-app (see [Cash Flow](#cash-payment-flow)) |
| `OTHER` | Defined by organizer. Same flow as digital transfers |

### Payment Status Flow

```
PENDING ──→ PROOF_SUBMITTED ──→ VERIFIED
                │
                ▼
             REJECTED ──→ PROOF_SUBMITTED (player resubmits)
```

### Cash Payment Flow

1. Player selects "Pay in cash" as their payment method.
2. `PlayerPayment` is created with status `PENDING` and method `CASH`.
3. On match day, the player delivers cash to the recipient (organizer or field staff).
4. The recipient confirms receipt in-app: "Cash received from [Player]".
5. Status changes to `VERIFIED`.

### Guest Player Payment Responsibility

When a registered player invites guests, **the inviter is financially responsible** for all their guests' payments:

- One `PlayerPayment` is created for the inviter's own share.
- One additional `PlayerPayment` is created per guest, with `responsiblePlayerId` pointing to the inviter.
- The app displays a consolidated total: *"You owe 30,000 COP total (10k for you + 10k for Guest 1 + 10k for Guest 2)"*.

---

## Guest Player System

### Overview

Registered players can invite non-registered friends to a match. Guest players occupy roster spots and are visible to all participants, but don't have full app profiles.

### Rules

1. Guest players count towards `currentQuantityPlayers` and `maxQuantityPlayers`.
2. The inviter is financially responsible for all their guests.
3. In the match player list, guests are displayed as: *"Guest of [Inviter Name]"*.
4. An optional phone number can be provided to send an invitation link (download prompt).

### Guest Status

| Status | Description |
| --- | --- |
| `INVITED` | Added to the match by a registered player |
| `CONFIRMED` | Attendance confirmed (by guest or inviter) |
| `NO_SHOW` | Did not attend the match |

---

## Notification System

### Notification Types

| Type | Recipient | Trigger | Description |
| --- | --- | --- | --- |
| `LOW_PLAYERS` | Organizer | Periodic, while `current < min` | Not enough players yet |
| `PAYMENT_REQUEST` | Players | 1 hour before match | Pay X to [recipient] via [method] |
| `MATCH_REMINDER` | Players | 45–30 min before match | Punctuality reminder, match is on |
| `MATCH_CANCELLED` | All participants | Organizer action | Match was cancelled |
| `MATCH_POSTPONED` | All participants | Organizer action | Match was postponed to new date |
| `PAYMENT_VERIFIED` | Payer | Receptor confirms | Your payment was verified |
| `PAYMENT_REJECTED` | Payer | Receptor rejects | Resubmit your proof |
| `PLAYER_JOINED` | Organizer | Player joins | A new player joined your match |
| `GUEST_ADDED` | Organizer | Inviter adds guest | A guest was added to your match |
| `RATE_PLAYERS` | Players | Match completed | Rate the players you played with |

### Notification Timeline

```
── Match Created ──────────────────────────────────────────────── Match Time ──→

 OPEN                          CONFIRMED       COLLECTING       MATCH
  │                               │                │              │
  ├─ LOW_PLAYERS (periodic) ──────┤                │              │
  │                               │                │              │
  │                               ├─ 1h before ───►│              │
  │                               │  PAYMENT_REQUEST              │
  │                               │                │              │
  │                               │    45-30 min ──┼──►           │
  │                               │    MATCH_REMINDER             │
  │                               │                │              │
  │                               │                │    ──► COMPLETED
  │                               │                │         RATE_PLAYERS
```

### Rules

- `MATCH_REMINDER` is sent between **45 and 30 minutes** before the match, depending on server availability.
- `MATCH_CANCELLED` and `MATCH_POSTPONED` can only be triggered before `COLLECTING_PAYMENTS`.
- For guest players, notifications are routed through their inviter.

---

## Rating System

### Overview

After a match is completed, all participants can rate the players they played with.

### Rules

1. Ratings are only enabled after the match reaches `COMPLETED` status.
2. A player can only rate others who participated in the **same match**.
3. Each rating includes a numeric score and an optional comment.
4. A player's overall `score` is the average of all ratings received across matches.
5. Guest players **cannot be rated** (they don't have a profile).

---

## Use Cases

### UC-01: Create a Match

**Actor:** Organizer (registered player)

1. Player enters match details: field, date, time, max/min players, total field cost, deposit amount.
2. Player provides field payment info and their own payment info (for reimbursements).
3. System creates the match with status `OPEN`.
4. System creates `MatchFinancials` with status `PENDING` and calculates `costPerPlayer`.

### UC-02: Join a Match

**Actor:** Registered player

1. Player browses available matches (status `OPEN`).
2. Player sends a join request with an optional comment and team preference.
3. Organizer reviews and accepts/rejects the request.
4. On acceptance, `currentQuantityPlayers` increments and `costPerPlayer` recalculates.

### UC-03: Invite a Guest Player

**Actor:** Registered player (inviter)

1. Inviter selects "Invite a friend" on the match page.
2. Inviter enters the guest's name and optional phone number.
3. System creates a `GuestPlayer` record with status `INVITED`.
4. `currentQuantityPlayers` increments and `costPerPlayer` recalculates.
5. Other participants see the guest listed as *"Guest of [Inviter]"*.
6. *(Optional)* System sends an SMS/WhatsApp with a download link.

### UC-04: Confirm a Match

**Actor:** Organizer

1. Organizer reviews the player list and decides the match will happen.
2. Organizer assigns which players will pay them (deposit reimbursement).
3. System transitions match to `CONFIRMED`.
4. System generates `PlayerPayment` records for all participants.

### UC-05: Collect Payments

**Trigger:** 1 hour before match time

1. System transitions match to `COLLECTING_PAYMENTS`.
2. System sends `PAYMENT_REQUEST` notifications to all players with: amount, recipient, and payment method.
3. Players submit payment proof (screenshot) or select cash.
4. Organizer (or field staff) verifies each payment.
5. On verification, player is notified with `PAYMENT_VERIFIED`.
6. On rejection, player is notified with `PAYMENT_REJECTED` and must resubmit.

### UC-06: Send Punctuality Reminder

**Trigger:** 45–30 minutes before match time (server availability)

1. System sends `MATCH_REMINDER` to all confirmed players.
2. Message confirms the match is still on and reminds punctuality.

### UC-07: Cancel a Match

**Actor:** Organizer
**Precondition:** Match is NOT in `COLLECTING_PAYMENTS` or later.

1. Organizer selects "Cancel match".
2. System transitions match to `CANCELLED`.
3. System sends `MATCH_CANCELLED` notification to all participants.
4. No monetary transactions have occurred — no refunds needed.

### UC-08: Postpone a Match

**Actor:** Organizer
**Precondition:** Match is NOT in `COLLECTING_PAYMENTS` or later.

1. Organizer selects "Postpone match" and provides a new date/time.
2. System transitions match to `POSTPONED`, then back to `OPEN` with updated schedule.
3. System sends `MATCH_POSTPONED` notification with the new date to all participants.

### UC-09: Rate Players After a Match

**Actor:** Registered player
**Precondition:** Match status is `COMPLETED`.

1. System sends `RATE_PLAYERS` notification to all registered participants.
2. Player opens the rating screen and sees the list of other participants.
3. Player assigns a score and optional comment to each.
4. System updates each rated player's average `score`.

### UC-10: Handle Cash Payment

**Actor:** Payment recipient (organizer or field staff)

1. Player selected `CASH` as payment method during `COLLECTING_PAYMENTS`.
2. On match day, player hands cash to the recipient.
3. Recipient opens the app and marks the payment as received.
4. System updates `PlayerPayment` status to `VERIFIED`.
