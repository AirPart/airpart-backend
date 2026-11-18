# Auth & RBAC PoC

Proof of concept for [ADR 0001](../knowledge-base/adr/0001-auth-rbac-stack.md):
Django 5.2 LTS + DRF + SimpleJWT + Casbin.

## Endpoints

| Method | Path                | Auth | Policy                                  |
| ------ | ------------------- | ---- | --------------------------------------- |
| POST   | `/api/auth/login`   | none | —                                       |
| POST   | `/api/auth/refresh` | none | —                                       |
| GET    | `/api/me`           | JWT  | —                                       |
| GET    | `/api/invoices`     | JWT  | `invoice` / `read` in the user's domain |

## Local run (SQLite)

```bash
cd app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Run with Docker (PostgreSQL)

```bash
docker compose up --build -d
docker compose exec web python manage.py seed_demo
```

## Try it

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"demo-pass-12345"}' | python -c 'import json,sys; print(json.load(sys.stdin)["access"])')

curl -s http://localhost:8000/api/me -H "Authorization: Bearer $TOKEN"
curl -s -i http://localhost:8000/api/invoices -H "Authorization: Bearer $TOKEN"   # 200
```

`bob` (sales in `branch_isfahan`) gets **403** on `/api/invoices`, because
`policy.csv` grants `invoice:read` only in `branch_tehran`.

## Tests

```bash
cd app
pytest -q
```

## Access model

`authz/model.conf` defines `sub, dom, obj, act` with a domain-scoped role
definition. `authz/policy.csv` holds the demo policy:

```
p, sales, branch_tehran, invoice, read
g, alice, sales, branch_tehran
```

The enforcer is cached per process; changing policy on disk needs a restart.
Dynamic policy storage (Casbin ORM adapter) is a follow-up, not part of this PoC.
