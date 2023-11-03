#!bin/bash

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists, skipping init"
    cd frappe-bench
    bench start
else
    echo "Creating new bench..."
fi

export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"

bench init --skip-redis-config-generation frappe-bench

cd frappe-bench

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis:6379
bench set-redis-queue-host redis:6379
bench set-redis-socketio-host redis:6379

# Remove redis, watch from Procfile
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

eval `ssh-agent -s`
ssh-add ~/.ssh/parameshnalla

bench get-app git@github.com:ajnacloud-ksj/india_api_compliance.git


bench new-site ajna.localhost \
--force \
--mariadb-root-password 123 \
--admin-password admin \
--no-mariadb-socket

bench --site ajna.localhost install-app india_api_compliance
bench --site ajna.localhost set-config developer_mode 1
bench --site ajna.localhost clear-cache
bench --site ajna.localhost set-config mute_emails 1
bench use ajna.localhost

bench start
