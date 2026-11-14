# mailonix-backend

Mailonix email security gateway (SMTP proxy, parser, checks, fusion, policy, delivery) aur baad mein API.
Frontend alag repo mein hai.

## Pehli dafa setup (Windows PowerShell)

Zaroorat: Python 3.11+, Git, Docker Desktop (WSL2).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
docker compose up -d
python -m pytest -q
```

Agar `Activate.ps1` par "running scripts is disabled" aaye, ek dafa yeh chalao, phir dobara activate:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Kya chal raha hai, kaise dekhein

| Cheez | Kahan |
| --- | --- |
| PostgreSQL | `localhost:5432` (user/pass/db: `mailonix`) |
| Mailpit inbox (web) | http://localhost:8025 |
| Mailpit SMTP | `localhost:1025` |

```powershell
docker compose ps                       # dono "healthy"/"running"
docker compose logs -f postgres         # masla ho to
docker compose down                     # band karna (data mehfooz)
docker compose down -v                  # band + database saaf
```

## Qaide (khulasa)

1. Check sirf `Signal` deta hai; email ko badalta ya rokta nahi.
2. Check database mein nahi likhta. Signals sirf orchestrator save karta hai.
3. `src/mailonix/contracts/` frozen hai (v1.0). Badlao se pehle tech lead se baat.
4. Naya table/column: pehle tech lead ko batao; migration ek hi banda banata hai.
5. Lab mein asli internet par bharosa nahi: `TI_MODE=mock`, `.test` domains, `.eml` replay.

## Branches

`main` protected hai. Kaam `feat/<wp>-<naam>` branch par, merge sirf PR se.
PR mein likho: kaise chalaya, kaun sa Signal DB mein dekha, kya contract ya enum badla.
