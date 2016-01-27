#!/bin/bash
# exit on error
#set -e
# output debug
set -x
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

[ -z "${BASH}" ] && {
    echo 'cannot execute the script, non-bash environment detected but bash is required for method like "export -f " '
    return 1
}

##  STUB ALL LSB-INIT FUNCTIONS
function_exists() {
    declare -f -F $1 > /dev/null
    return $?
}

function_exists "log_daemon_msg" || {
    # stub
    log_daemon_msg(){
    echo log_daemon_msg ">>" $@
    }
    export -f log_daemon_msg
}

function_exists "log_progress_msg" || {
    # stub
    log_progress_msg(){
    echo log_progress_msg ">>" $@
    }
    export -f log_progress_msg
}

function_exists "log_failure_msg" || {
    # stub
    log_failure_msg(){
    echo log_failure_msg ">>" $@
    }
    export -f log_failure_msg
}
function_exists "log_end_msg" || {
    # stub
    log_end_msg(){
    echo log_end_msg ">>" $@
    }
    export -f log_end_msg
}

export DISABLED_CONFIG_VALIDATION=1

export COMPOSE_INITD_FILE=$DIR'/../src/docker-compose-initd.sh'
load_dockerinitd_includes(){
    . $COMPOSE_INITD_FILE
}
export -f load_dockerinitd_includes

#. $DIR/resources/initd/cs-sample.sh status
echo "--------------- starting "
bash $DIR/resources/initd/cs-sample.sh start
app_status=$?
echo "app_status = $app_status "

echo "--------------- status "
bash $DIR/resources/initd/cs-sample.sh start
app_status=$?
echo "app_status = $app_status "

exit 0