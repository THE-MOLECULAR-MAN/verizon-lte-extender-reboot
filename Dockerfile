# manually forcing x86_64 (amd64) architecture instead of the local one
# even the --platform= with buildx didn't work on Apple M1
FROM --platform=linux/amd64 alpine:3.17.3

# FROM alpine:3.17.3        # this causes issues when built on Apple M1
# FROM python:3.6-alpine    # was considering this for the future

LABEL version=“0.6.0”
USER root
ENV RUNNING_IN_DOCKER_CONTAINER True
RUN adduser -S pythonapp
WORKDIR /app

# Copy over the files
# https://docs.docker.com/engine/reference/builder/#copy
COPY --chown=pythonapp --chmod=0744 [".env", "start_python_script.sh", "soft_reboot_verizon_4g_repeater.py", "requirements.txt", "/app"]
COPY --chown=root --chmod=0644 ["cron-pythonapp-user", "/etc/cron.d/cron-pythonapp-user"]

# create log file and set perms on it
RUN touch /var/log/cron.log && chown pythonapp /app /var/log/cron.log && chmod 777 /var/log/cron.log

# install the crontab
RUN /usr/bin/crontab -u pythonapp /etc/cron.d/cron-pythonapp-user

# start the cron service and watch the log
CMD /usr/sbin/crond -f -l 8 && tail -f /var/log/cron.log

# Install python/pip
# cannot move this, must stay under current root user
ENV PYTHONUNBUFFERED=1
# curl>=7.88.1
# must use alpine-conf, not tzdata package
# supercronic=0.2.1-r7 breaks in multi-arch, can't specify version
RUN apk add --update --no-cache python3=3.10.11-r0 curl supercronic shadow=4.13-r0 busybox-suid=1.35.0-r29 alpine-conf=3.15.1-r1
RUN ln -sf python3 /usr/bin/python && python3 -m ensurepip
RUN pip3 install --no-cache-dir --no-cache --upgrade -r requirements.txt

# change docker container to use local hosts's time zone
# define the timezone, used for cron
# more reliable than using vol mounts since that can vary with Host OS
# https://wiki.alpinelinux.org/wiki/Alpine_setup_scripts#setup-timezone
RUN setup-timezone -z America/New_York

# gotta manually install the webdriver for Chrome
RUN echo "http://dl-cdn.alpinelinux.org/alpine/v3.17/community" > /etc/apk/repositories && echo "http://dl-cdn.alpinelinux.org/alpine/v3.17/main" >> /etc/apk/repositories && apk update

# adds about 500 MB of files to docker image
RUN apk add --no-cache chromium-chromedriver
#=112.0.5615.49-r0

# RUN rm -Rf /var/cache/apk/*

# the following line BREAKS things:
# USER pythonapp
