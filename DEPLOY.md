# Deploy (Render — free tier)

One-platform deploy of the whole stack on Render, keeping the **Next.js proxy**
architecture: the browser only talks to the Next.js origin, which reverse-proxies
`/api/*` to Django. This is what lets the `SameSite=Strict` refresh cookie work.

```
Browser ──▶ taskapp-frontend (Next.js, Node)  ──proxy /api/*──▶ taskapp-backend (Django, Docker)
                                                                        │
                                                                 taskapp-db (Postgres)
                                                                 S3 / R2 (image attachments)
```

Everything below is manual dashboard work + pasting env values. Infra is declared in
[`render.yaml`](render.yaml); CD is [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

---

## 0. Prerequisites (accounts to create)

- **Render** account (no credit card needed for free tier).
- An **S3-compatible bucket** for image attachments — **Cloudflare R2** recommended
  (10 GB free forever). AWS S3 works too (free only 12 months).
- *(Optional)* an **SMTP** provider for real emails (e.g. Brevo — 300/day free).
  Without it, notification emails just print to the backend logs.

---

## 1. Create the object storage (do this first — the backend won't boot without it)

**Cloudflare R2:**
1. Cloudflare dashboard → **R2** → *Create bucket* (e.g. `taskapp-media`).
2. **R2 → Manage API Tokens → Create** → note the **Access Key ID** + **Secret**.
3. Your endpoint is `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`.

Keep these four values for step 3: bucket name, access key, secret, endpoint URL.

## 2. Launch the Blueprint

1. Push this branch to GitHub and get it onto `master`.
2. Render → **New → Blueprint** → pick this repo. Render reads `render.yaml` and
   proposes: `taskapp-db`, `taskapp-backend`, `taskapp-frontend`.
3. Apply. Render creates all three. The backend will fail its first boot until the
   env vars in step 3 are set — that's expected.

## 3. Fill the environment variables

### `taskapp-backend` (Render → service → Environment)

| Key | Value | Notes |
|-----|-------|-------|
| `DJANGO_SETTINGS_MODULE` | `core.settings.production` | preset by blueprint |
| `DJANGO_SECRET_KEY` | *(auto-generated)* | preset by blueprint |
| `DB_*` | *(auto-wired from `taskapp-db`)* | preset by blueprint |
| `AWS_STORAGE_BUCKET_NAME` | your bucket name | **required** |
| `AWS_ACCESS_KEY_ID` | R2/S3 access key | **required** |
| `AWS_SECRET_ACCESS_KEY` | R2/S3 secret | **required** |
| `AWS_S3_REGION_NAME` | `auto` for R2, e.g. `ap-southeast-1` for AWS | |
| `AWS_S3_ENDPOINT_URL` | R2 endpoint URL | **leave blank for real AWS S3** |
| `CSRF_TRUSTED_ORIGINS` | `https://taskapp-frontend.onrender.com` | the **frontend** origin |
| `CORS_ALLOWED_ORIGINS` | `https://taskapp-frontend.onrender.com` | same |
| `FRONTEND_URL` | `https://taskapp-frontend.onrender.com` | email deep links |
| `ALLOWED_HOSTS` | *(optional)* | the Render host is trusted automatically |

### `taskapp-frontend`

| Key | Value | Notes |
|-----|-------|-------|
| `BACKEND_INTERNAL_URL` | `https://taskapp-backend.onrender.com` | the backend's public URL |
| `NODE_VERSION` | `20` | preset by blueprint |

> **Ordering:** the frontend build **bakes** `BACKEND_INTERNAL_URL` into the proxy at
> build time. Set it *before* the first frontend deploy. Flow: backend deploys →
> copy its URL → set `BACKEND_INTERNAL_URL` and the backend's `*_ORIGINS`/`FRONTEND_URL`
> to the frontend URL → redeploy both.

### *(Optional)* real email on `taskapp-backend`

| Key | Value |
|-----|-------|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | from your SMTP provider |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `no-reply@yourapp.com` |

## 4. Continuous deployment (tag-based, CI-gated)

Deploys fire from GitHub Actions **when you push a version tag** — and only after the
full CI suite passes on that exact commit, so a red build never ships. Wire it up once:

1. Render → each service → **Settings → Deploy Hook** → copy the URL (one per service).
2. GitHub repo → **Settings → Secrets and variables → Actions → New secret**:
   - `RENDER_DEPLOY_HOOK_BACKEND` = backend deploy hook URL
   - `RENDER_DEPLOY_HOOK_FRONTEND` = frontend deploy hook URL

Cutting a release from then on:

```bash
git checkout master && git pull
git tag v1.0.0            # bump per release
git push origin v1.0.0
```

The tag triggers `deploy.yml` → it reuses the CI pipeline (lint + test + e2e) on the
tagged commit → on green, both services redeploy. Plain pushes to `master` still run
CI for validation but no longer deploy.

---

## Known limitations on the free tier

- **Cold starts:** free web services sleep after 15 min idle; the next request waits
  ~30–60 s. Open both URLs a minute before a demo to warm them.
- **Postgres expires 30 days** after creation (fine for a short demo; back up if needed).
- **Scheduled jobs are not deployed.** `flip_overdue_tasks` and `send_task_reminders`
  (the `cron` service in `docker-compose.yml`) need an always-on worker, which isn't
  free on Render. Run them by hand from **Render → backend → Shell** when needed:
  ```
  python manage.py flip_overdue_tasks
  python manage.py send_task_reminders
  ```
