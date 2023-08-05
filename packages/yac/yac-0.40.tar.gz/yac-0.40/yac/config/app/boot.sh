#!/bin/bash

# Bootrap a new AWS instance into a YAC CoreOS host

# format volumes as an ext4 fs
mkfs -t ext4 /dev/xvdc
mkfs -t ext4 /dev/xvdd

# create the app home and docker lib directories
# each will become the mount points on the volumes above.
mkdir -p /var/local/atlassian
mkdir -p /var/lib/docker

# mount the volumes
mount /dev/xvdc /var/lib/docker
mount /dev/xvdd /var/local/atlassian

# the APP_NAME variable is used in a few paths
# make sure it is lower case
APP_NAME_LC=${APP_NAME,,}

# create the home dir for the app
mkdir /var/local/atlassian/$APP_NAME_LC

# create the directory for backups to log to
mkdir /var/local/atlassian/$APP_NAME_LC/backup-logs
		
# change owner to daemon
chown -R daemon:daemon /var/local/atlassian/$APP_NAME_LC

# give r/w/x(traversal) to everyone on app home
chmod 0777 -R /var/local/atlassian/$APP_NAME_LC

# configure NTP

if [ $NTP_SERVERS ]; then
	# break existing symbolic link to shared conf file 
	rm /etc/ntp.conf
	# write the servers into a new conf file. servers are in a semicolon delimitted string. 
	# sed 'em into a conf file with one line per server
	echo $NTP_SERVERS | sed -e 's/;/\n/g' | sed -e 's/^/server /' > /etc/ntp.conf
	chmod 0666  /etc/ntp.conf
	# restart the ntp daemon so it picks up the new configs
	systemctl restart ntpd
fi

# set timezone
timedatectl set-timezone America/Los_Angeles

if [ $PROXY_NAME ] && [ $PROXY_PORT ]; then
	# download and configure http-proxy.conf, which tells docker how to navigate our proxyß
	mkdir -p /etc/systemd/system/docker.service.d
	wget --no-check-certificate -O /etc/systemd/system/docker.service.d/http-proxy.conf -q $DOWNLOAD_URL/http-proxy.conf?$REPO_TAG
	chown core:core /etc/systemd/system/docker.service.d/http-proxy.conf
	chmod 0644      /etc/systemd/system/docker.service.d/http-proxy.conf
	sed -i -e "s/{{PROXY_NAME}}/$PROXY_NAME/g" /etc/systemd/system/docker.service.d/http-proxy.conf
	sed -i -e "s/{{PROXY_PORT}}/$PROXY_PORT/g" /etc/systemd/system/docker.service.d/http-proxy.conf
fi

# download and configure docker-tcp.socket, which enables Docker's remote API on http
wget --no-check-certificate -O /etc/systemd/system/docker-tcp.socket -q $DOWNLOAD_URL/docker-tcp.socket?$REPO_TAG
chown core:core /etc/systemd/system/docker-tcp.socket
chmod 0644      /etc/systemd/system/docker-tcp.socket

# reload and restart docker to pick up with the new proxy and docker configurations
systemctl enable docker-tcp.socket
systemctl stop docker
systemctl daemon-reload
systemctl start docker-tcp.socket
systemctl start docker

if [ $EFS_ID ] && [ $MOUNT_DIR ]; then
	# configure the NFS mount if EFS identifier and mount directory were specified
	mkdir -p /efs/$MOUNT_DIR
	chmod 777 /efs/$MOUNT_DIR
	mount -t nfs4 $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone).$EFS_ID.efs.us-west-2.amazonaws.com:/ /efs
	mkdir -p /var/local/atlassian/$APP_NAME_LC/$MOUNT_DIR
	mount --bind /efs/$MOUNT_DIR/ /var/local/atlassian/$APP_NAME_LC/$MOUNT_DIR
fi

if [ $RESTORE_CONFIG ] && [ $HOST_NAME ]; then
	# restore any home directory files that this instance should have at startup
	docker run --name restore-at-boot \
	--detach=true \
	--volume=/var/local/atlassian/$APP_NAME_LC:/var/local/atlassian/$APP_NAME_LC:rw \
	--volume=/var/local/atlassian/$APP_NAME_LC/backup-logs:/var/local/backups:rw \
	nordstromsets/backups:latest \
	python -m src.restore $RESTORE_CONFIG $HOST_NAME
fi

if [ $CLUSTER_NAME ]; then

	# install ECS agent and register this instance with the CLUSTER_NAME cluster
	docker run --name ecs-agent \
	--detach=true \
	--restart=on-failure:10 \
	--volume=/var/run/docker.sock:/var/run/docker.sock \
	--volume=/var/log/ecs/:/log \
	--volume=/var/lib/ecs/data:/data \
	--volume=/sys/fs/cgroup:/sys/fs/cgroup:ro \
	--volume=/var/run/docker/execdriver/native:/var/lib/docker/execdriver/native:ro \
	--publish=127.0.0.1:51678:51678 \
	--env=ECS_LOGFILE=/log/ecs-agent.log \
	--env=ECS_LOGLEVEL=info \
	--env=ECS_DATADIR=/data \
	--env=ECS_CLUSTER=$CLUSTER_NAME \
	amazon/amazon-ecs-agent:latest
fi
