# The live warm-up WordPress target

The toy app runs on its own (`docker compose up -d toydb`, port 8880). The WordPress
target is the one real app we crack together as the warm-up. Standing it up takes a few
extra steps because WordPress needs a database and an install.

1. Start the stack:
   ```
   docker compose -f targets/docker-compose.yml up -d
   ```
2. Install WordPress and the warm-up plugin with wp-cli (WP-Polls is unauthenticated, so
   the probe works with no login):
   ```
   docker compose -f targets/docker-compose.yml exec wordpress bash -lc '
     cd /var/www/html
     wp core install --url=http://127.0.0.1:8881 --title=Lab \
       --admin_user=admin --admin_password=admin --admin_email=a@b.test --allow-root
     wp plugin install https://downloads.wordpress.org/plugin/wp-polls.2.77.2.zip \
       --activate --allow-root
   '
   ```
3. The app serves on http://127.0.0.1:8881.

The other targets are source-read: `bash scripts/fetch_targets.sh` puts their code under
`targets/src/`. Students hunt those blind and confirm against the upstream fix at the
debrief. The instructor key (`../../sql-injection-key/`) has the sink and a safe probe for
each target.
