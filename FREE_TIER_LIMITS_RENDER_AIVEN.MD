# Free-tier limits: Render (web service) & Aiven (MySQL)

**Date checked:** 2026-07-29
**Checked by:** Michał Misiewicz
**Sources:** Official documentation only (`render.com/docs`, `aiven.io/docs`)

---

## Render — Free web service

Source: [render.com/docs/free](https://render.com/docs/free)

| Aspect | Limit |
|---|---|
| Spin-down | Spins down after **15 minutes** with no inbound traffic (HTTP or WebSocket). Restarts on next request; restart takes **~1 minute**. Render shows a loading page to the browser during spin-up. |
| Ephemeral filesystem | **Confirmed.** Any local filesystem changes (uploaded files, local SQLite, etc.) are lost on every redeploy, restart, **or spin-down**. Free instances cannot attach a persistent disk (paid-only feature). |
| Monthly compute | **750 free instance hours** per workspace per month. Spun-down time doesn't count against this. If exhausted, all free web services are suspended until the next calendar month (no rollover). |
| Bandwidth / build minutes | Free services count against the workspace's monthly included bandwidth and build-pipeline minutes. Exceeding these triggers billing (if a payment method is on file) or suspension (if not). |
| Other restrictions relevant to us | No SSH/shell access on free instances; no horizontal scaling; can't receive private-network traffic (can still send to same-region datastores); Render may restart a free instance at any time for maintenance. |
| Credit card | Not required to create a free web service. |

**Why this matters for us:** the backend must not rely on the local filesystem
for anything we need to keep (session state, uploaded files, a local SQLite
fallback, etc.) — it will disappear on every idle spin-down, not just on
redeploy. Since we're pairing this with an external Aiven MySQL database, this
should be fine as long as the app doesn't write anything to disk it expects to
survive a restart.

---

## Aiven — Free MySQL

Source: [aiven.io/docs/products/mysql/concepts/mysql-free-tier](https://aiven.io/docs/products/mysql/concepts/mysql-free-tier)
(page last updated by Aiven: 2026-03-13)

| Aspect | Limit |
|---|---|
| Storage | **1 GB** disk |
| RAM | **1 GB** |
| CPU | 1 CPU (single node — no high availability, no replicas) |
| Credit card | **Not required** to sign up or use the free tier. |
| Time limit | **None** — the free service itself doesn't expire. |
| Inactivity policy | Aiven may **power off** the service (a) if there's no initial usage within the first few hours of creation, or (b) after a period of continued inactivity. Aiven sends a notification before powering off for inactivity. The service can be **powered back on manually at any time** — no data loss from a power-off, unlike Render's ephemeral-filesystem spin-down. |
| Other limitations | No VPC support, no static IPs, no integrations, no forking, no paid support, only one free instance per service type per organization, **not covered by Aiven's 99.99% SLA**. |
| Backups | Included, even on the free tier. |

**Why this matters for us:** unlike Render's spin-down (which wipes local
disk), an Aiven free-tier power-off is **not destructive** — data isn't lost,
the service just needs to be manually restarted from the console. The main
practical risk is that if the database is powered off due to inactivity and
nobody notices, a demo or smoke test could fail until someone manually
restarts it in the Aiven console.

---

## Combined risk to flag

Both free tiers can independently go idle: Render's web service spins down
after 15 minutes, and Aiven's MySQL instance can be powered off after a
longer period of inactivity. For **T-62 (MySQL smoke-test)** and any later
demo, this means:
- The **first request** after idle time will be slow (Render cold start ~1
  min) — expected, not a bug.
- If the **Aiven database** has also been powered off, the backend will fail
  to connect until someone manually powers it back on in the Aiven console —
  this does **not** happen automatically like Render's web service.

**Recommendation:** before any demo or scheduled smoke test, manually check
the Aiven console to confirm the MySQL instance is powered on, since — unlike
Render — it will not wake itself up on request.

---

## Blockers

None identified that would prevent starting T-62. Flagging the combined
idle/power-off behavior above to the supervisor as a process note (manual
check before demos), not a hard blocker — raised before day 18 per the
acceptance criteria.