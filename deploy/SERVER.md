# Running the shop on a server (e.g. hugcrafts.am)

Apache handles https and sends the built files and photos itself. Everything else goes to
Django (gunicorn): pages, `robots.txt`, `sitemap.xml`, `/api/` and `/admin/`. Pages must go
to Django, which adds each page's title, description, language links and text for search
engines. If Apache sends `index.html` itself, search engines see an empty page.

## 1. Settings in `backend/.env`

```ini
DEBUG=False
SITE_URL=https://hugcrafts.am
ALLOWED_HOSTS=hugcrafts.am,www.hugcrafts.am
CSRF_TRUSTED_ORIGINS=https://hugcrafts.am,https://www.hugcrafts.am
BEHIND_PROXY=True
SECURE_SSL_REDIRECT=True
# After a week or two with https working everywhere, add this as well (browsers remember it):
# SECURE_HSTS_SECONDS=31536000
```

What each line does:
- **`SITE_URL`**: every link and image address uses `https://hugcrafts.am`.
- **`www` in `ALLOWED_HOSTS`**: `www.hugcrafts.am` is answered with a redirect to `hugcrafts.am`. It also needs a DNS record: an `A` record for `www` with the same IP as `hugcrafts.am`.
- **`BEHIND_PROXY` and `SECURE_SSL_REDIRECT`**: `http://` addresses are redirected to `https://`. They only work together with `X-Forwarded-Proto` in the Apache config below. Without it, pages keep redirecting to themselves.

## 2. Apache

Modules needed: `sudo a2enmod ssl proxy proxy_http headers`. Replace `/srv/CelebCandles`
with the project folder and keep your own certificate lines. Gunicorn should listen only on
`127.0.0.1:8000`, so nobody can reach it without going through Apache.

```apache
<VirtualHost *:80>
    ServerName hugcrafts.am
    ServerAlias www.hugcrafts.am
    Redirect permanent / https://hugcrafts.am/
</VirtualHost>

<VirtualHost *:443>
    ServerName hugcrafts.am
    ServerAlias www.hugcrafts.am
    # SSLEngine on, SSLCertificateFile …, SSLCertificateKeyFile … (as you have them now)

    # Built JavaScript/CSS: the file names change on every build, so browsers keep them a year.
    Alias /assets/ /srv/CelebCandles/frontend/dist/assets/
    <Directory /srv/CelebCandles/frontend/dist/assets>
        Require all granted
        Header set Cache-Control "public, max-age=31536000, immutable"
    </Directory>

    # Uploaded photos and videos: kept 30 days (a new upload always gets a new file name).
    Alias /media/ /srv/CelebCandles/backend/media/
    <Directory /srv/CelebCandles/backend/media>
        Require all granted
        Header set Cache-Control "public, max-age=2592000"
    </Directory>

    # The admin's own CSS and JavaScript (python manage.py collectstatic).
    Alias /static/ /srv/CelebCandles/backend/staticfiles/
    <Directory /srv/CelebCandles/backend/staticfiles>
        Require all granted
        Header set Cache-Control "public, max-age=86400"
    </Directory>

    # Smaller downloads for text files.
    AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml text/plain

    # Everything else goes to Django.
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    ProxyPass /assets/ !
    ProxyPass /media/ !
    ProxyPass /static/ !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Then `sudo apachectl configtest`, and if it says `Syntax OK`, run `sudo systemctl reload apache2`.

## 3. After each update

```bash
cd /srv/CelebCandles/frontend && npm ci && npm run build
cd ../backend && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# then restart gunicorn, e.g. sudo systemctl restart gunicorn
```

## 4. Check it

```bash
curl -I http://hugcrafts.am/            # 301 -> https://hugcrafts.am/
curl -I https://www.hugcrafts.am/       # 301 -> https://hugcrafts.am/
curl -s https://hugcrafts.am/robots.txt # ends with the sitemap address
curl -s https://hugcrafts.am/en | grep "<title"           # the English home page title
curl -I https://hugcrafts.am/no-such-page                # 404
curl -I https://hugcrafts.am/assets/<a file from dist/assets> | grep -i cache-control
curl -s https://hugcrafts.am/api/candles/ | grep -o '"image":"[^"]*"' | head -2   # https://
```
