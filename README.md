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
alembic upgrade head
python -m pytest -q
```

## Roz kaam shuru karte waqt

Laptop restart ke baad Docker Desktop khud nahi khulta. Pehle Docker Desktop kholo, phir:

```powershell
docker compose ps        # postgres "Up (healthy)", mailpit "Up"
```

Tests mein "PostgreSQL nahi mila" aaye to sab se pehle yahi dekho.

Agar `Activate.ps1` par "running scripts is disabled" aaye, ek dafa yeh chalao, phir dobara activate:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Database migrations (Alembic)

Tables `src/mailonix/db/models.py` mein hain. Migration sirf ek banda banata hai (tech lead se pooch kar).

```powershell
alembic upgrade head                              # saari migrations lagao
alembic current                                   # abhi kaun si lagi hai
alembic revision --autogenerate -m "kya badla"    # models badalne ke baad nayi migration
alembic check                                     # models aur DB mein farq? "No new upgrade operations" = theek
```

## Checks

Har check `ParsedEmail` leta hai aur `Signal` deta hai. Saancha `src/mailonix/checks/base.py` mein, list `registry.py` mein.

```powershell
python scripts/show_checks.py              # saare checks ek namoona email par: kaun kya kehta hai
python scripts/show_checks.py --mismatch   # Reply-To alag domain wali email par
```

**Naya check jorna (ya placeholder ko asli banana):**
1. `src/mailonix/checks/` mein file (maslan `links.py`), class `Check` se: `name`, `group`, `default_params`, `async def run(email) -> Signal`.
2. Signal `self.ok(value, reasons, details)`, `self.abstain(...)` ya `self.unavailable(...)` se banao. Pata na ho to `abstain`, kabhi "0 = safe" nahi.
3. Naya check ho to `registry.py` ki `ALL_CHECKS` mein ek line.
4. Badalne wali values code mein nahi: `config/checks.toml` mein `[check_ka_naam]` ke neeche.
5. Test `tests/` mein, `make_email(...)` fixture se (bina parser ke email). Check kabhi database mein nahi likhta.

**Check band karna** (ablation, ya toota check): `.env` mein `DISABLED_CHECKS=intent,links`. Ek dafa ke liye:

```powershell
$env:DISABLED_CHECKS="intent"; python scripts/show_checks.py; Remove-Item Env:DISABLED_CHECKS
```

## Kya chal raha hai, kaise dekhein

| Cheez | Kahan |
| --- | --- |
| PostgreSQL | `localhost:5433` (user/pass/db: `mailonix`) |
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
