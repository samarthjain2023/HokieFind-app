# HokieFind Web — UI Kit

A high-fidelity click-through of the HokieFind Flask app, recreated from the
templates in `frontend/*.html`. Not production code — the job is to give a
designer or agent modular, brand-correct pieces to compose new screens.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The click-through prototype — drop in a browser and it runs |
| `kit.css` | Component styles (imports `../../colors_and_type.css` for tokens) |
| `Primitives.jsx` | `NavBar`, `Field`, `TextArea`, `Card`, `Badge`, `Message`, `PageHeader` |
| `Listings.jsx` | `ListingRow`, `ClaimRow` — the repeat units of the app |
| `Screens.jsx` | `LoginScreen`, `SignUpScreen`, `ListingsScreen`, `ClaimFormScreen`, `ClaimsListScreen`, `AccountScreen`, `ReportsScreen`, `AdminScreen` |

## Screens covered

Maps 1:1 onto the Flask templates:

- `LoginScreen` ← `frontend/login.html`
- `SignUpScreen` ← `frontend/sign_up.html`
- `ListingsScreen` ← `frontend/index.html` (home + add listing + list)
- `ClaimFormScreen` ← `frontend/claim_form.html`
- `ClaimsListScreen` ← `frontend/claims.html`
- `AccountScreen` ← `frontend/account.html`
- `ReportsScreen` ← `frontend/reports.html`
- `AdminScreen` ← `frontend/admin.html`

Edit screen (`frontend/edit.html`) is intentionally omitted — the form is
trivially a reuse of the Add Listing form.

## Interaction flow the demo supports

1. **Login** (any email/password) → lands on Listings.
2. **Add a listing** via the form at the top — updates the list, shows
   success flash.
3. **Claim** a listing → opens the claim form, submit returns to Listings.
4. **View claims** jumps to the claims list.
5. **Account** shows your listings + password change form.
6. **Reports** shows Most Active Finders + Active Claims tables.
7. **Admin** shows Create User form.
8. **Logout** returns to Login.

A sticky demo banner at the top lets you jump to any screen regardless of
flow state.

## Deviations from the codebase (intentional)

- **Typography upgraded** from `Arial` to Source Sans 3 / Source Serif 4.
  Flagged in the root README.
- **Burnt Orange accent** added for the Claim CTA and focus rings —
  the existing code only uses maroon. This is the core value add.
- **Navbar mark** has an orange corner-notch — brand anchor that didn't
  exist before.
- **Status badges** added to listings & claims (the Flask code had no
  visual status indicator at all).

## Running standalone

Open `index.html` directly in a browser, or serve the folder with any
static server. Requires network access for React / Babel from unpkg.
