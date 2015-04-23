#!/bin/bash

# . /lib/lsb/init-functions


#DESC=${DESC:"docker-compose initd manager"}


# default settings
[ -z "$DOCKER_COMPOSE_BIN_PATH" ] && {
    DOCKER_COMPOSE_BIN_PATH=$(which docker-compose)
}
[ -z "$YML_template_PATH" ] && {
    YML_template_PATH=$(pwd)
}
[ -z "$YML_filename" ] && {
    YML_filename=$(echo "docker-compose.yml")
}

[ -z "$NAME" ] &&  {
    NAME=$(basename $YML_template_PATH)
}

EXPECTED_CONTAINERS_COUNT=0 # must be recalculated



do_validate_config() {
    [ -x "$DOCKER_COMPOSE_BIN_PATH" ]|| {
        log_failure_msg "[ERROR]  docker-compose binary path [$DOCKER_COMPOSE_BIN_PATH] does not exists or isn't executable "
        return 1
    }

    [ -d "$YML_template_PATH" ] || {
        log_failure_msg "[ERROR]  YML_template_PATH [$YML_template_PATH] directory does not exists "
        return 1
    }

    [ -r "$YML_template_PATH/$YML_filename" ] || {
        log_failure_msg "[ERROR]  YML_template_PATH/YML_filename [$YML_template_PATH/$YML_filename] is not a readable file"
        return 1
    }

    EXPECTED_CONTAINERS_COUNT=$(get_expected_containers_names | wc -l )
    [ "$EXPECTED_CONTAINERS_COUNT" -lt "1" ] &&  {
        log_failure_msg "[ERROR]  cannot establish amount of expected containers"
        return 1
    }

}


get_expected_containers_names(){
    cat "$YML_template_PATH/$YML_filename" | awk '$0 ~ "^([a-zA-Z0-9]+):.*$" {print $0}'| awk '$0 ~ "^([a-zA-Z0-9]+):.*$" {print $0}' | sed -e  's/^\([^:]*\)\(:\)/\1/g'
}

# return created container from docker compose ( both running and stopped)
get_actual_containers_ids(){
    cd "$YML_template_PATH"
    $DOCKER_COMPOSE_BIN_PATH -f $YML_filename  ps -q
}


getNonRunningAppContainersCount(){
    docker inspect -f {{.State.Running}} `get_actual_containers_ids` | grep -i "false" | wc -l
}

compose_appTaks_rebuild(){
    log_progress_msg "rebuilding entire $YML_filename structure"
    cd "$YML_template_PATH"
    $DOCKER_COMPOSE_BIN_PATH -f $YML_filename  up -d
    app_rebuild_status=$?
    log_progress_msg "app rebuild status = $app_rebuild_status"

    return $app_rebuild_status
}


compose_appTaks_softRebuild(){
    log_progress_msg "rebuilding missing services from $YML_filename"
    cd "$YML_template_PATH"
    $DOCKER_COMPOSE_BIN_PATH -f $YML_filename  up -d --no-recreate
}

# return 0 if app is running ok,
# return 1 if expected container created count do not match
# return 2 if containers are not all running
is_entire_compose_app_running(){
    composeCreatedContainers=$(get_actual_containers_ids | wc -l)
    composeExpectedContainers=$(get_expected_containers_names | wc -l)
    [ "$composeCreatedContainers" -eq "$composeExpectedContainers" ] || {
        return 1 # if expected container created count do not match
    }

    [ "$(getNonRunningAppContainersCount)" -eq "0" ] || {
        return 2 # if expected container created count do not match
    }

    return 0 # OK
}

compose_app_start(){
    log_daemon_msg "Starting docker compose app" "compose"

    log_progress_msg "Starting docker compose app , total containers expected = $EXPECTED_CONTAINERS_COUNT "
    cd "$YML_template_PATH"
    $DOCKER_COMPOSE_BIN_PATH -f $YML_filename start

    is_entire_compose_app_running
    app_running_status=$?
    [ $app_running_status -ne 0 ] && {
        log_progress_msg "app is not running, starting now a soft rebuild"
        compose_appTaks_softRebuild
    }

    is_entire_compose_app_running
    app_running_status=$?
    [ $app_running_status -ne 0 ] && {
        log_progress_msg "app soft rebuild failed, start now a full compose rebuild"
        compose_appTaks_rebuild
    }

    is_entire_compose_app_running
    app_running_status=$?
    log_end_msg $app_running_status

    return $app_running_status
}


compose_app_reload(){
 log_daemon_msg "Reloading ( destroy and rebuild )  docker compose app" "compose"
 cd "$YML_template_PATH"
 log_progress_msg "Stopping containers"
 $DOCKER_COMPOSE_BIN_PATH -f $YML_filename stop

 log_progress_msg "Deleting cached containers containers"
 $DOCKER_COMPOSE_BIN_PATH -f $YML_filename rm --force

 log_progress_msg "Rebuilding containers"
 compose_appTaks_rebuild

 app_rebuild_status=$?
 log_end_msg $app_stopping_status
 return $app_stopping_status
}


compose_app_stop(){
 log_daemon_msg "Stopping docker compose app" "compose"
 cd "$YML_template_PATH"
 $DOCKER_COMPOSE_BIN_PATH -f $YML_filename stop
 app_stopping_status=$?
 log_end_msg $app_stopping_status
 return $app_stopping_status
}

compose_app_status(){
 log_daemon_msg "Checking running status of docker compose app" "compose"
 is_entire_compose_app_running
 app_running_status=$?
 log_end_msg $app_running_status
 return $app_running_status
}

compose_app_restart(){
 log_daemon_msg "Restarting docker compose app" "compose"
 compose_app_stop
 compose_app_start
}


[ -z "$DISABLED_CONFIG_VALIDATION" ] && {
do_validate_config
}


# docker-compose ps -q # show docker compose ids ( also of the stopped containers )

#
#case "$1" in
#  start)
#        compose_app_start
#        exit $?
#        ;;
#  stop)
#        compose_app_stop
#        exit $?
#        ;;
#
#  reload|force-reload)
#        compose_app_reload
#        exit $?
#        ;;
#
#  restart)
#        compose_app_restart
#        exit $?
#        ;;
#
#  status)
#        compose_app_status
#        exit $? # notreached due to set -e
#        ;;
#  *)
#        echo "Usage: {start|stop|reload|force-reload|restart|status}"
#        exit 1
#esac
#
#exit 0
