# Sharing the shop from this PC

`start-public.ps1` publishes the whole shop (site, admin, images) from this PC through a
free **Cloudflare quick tunnel**, and prints a public link like
`https://some-random-words.trycloudflare.com` that works on any phone or computer.

## Start sharing

In PowerShell, from the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File deploy\start-public.ps1
```

Wait for the line with `https://….trycloudflare.com` and share that link.
Press **Ctrl+C** in that window to stop sharing.

Add `-SkipBuild` to start faster when the frontend hasn't changed.

## Good to know

- **The link changes every time** the script starts, and the site is only online while this
  PC is on, awake and the window is open. For a permanent address, set up a named Cloudflare
  Tunnel with your own domain, or move to a hosting service.
- **Production mode**: the script runs Django with `DEBUG` off, served by Waitress on
  `127.0.0.1:8080`, which only this PC can reach. The tunnel is the only way in, so no router
  or firewall changes are needed. `backend/.env` keeps your development settings, and the
  development servers (ports 8000 and 5173) keep working side by side.
- **Admin**: `https://<your-link>/admin/`. Anyone with the link can reach the login page, so
  use a strong password (`python manage.py changepassword admin` in `backend/`).
- **Changes** made in the admin show up immediately. After changing frontend code, restart
  the script (without `-SkipBuild`) so the site is rebuilt.
- Uploaded images are served by Django itself, which is fine for a small shop on one PC.

## What the script does

1. `npm run build` in `frontend/`, which writes `frontend/dist`.
2. `manage.py migrate` and `collectstatic` in `backend/`.
3. Starts Waitress with production settings, set for that window only: `DEBUG=False`,
   `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS=https://*.trycloudflare.com`, `BEHIND_PROXY`,
   `SERVE_MEDIA`.
4. `cloudflared tunnel --url http://127.0.0.1:8080`.

`cloudflared` was installed with `winget install --id Cloudflare.cloudflared -e`.
