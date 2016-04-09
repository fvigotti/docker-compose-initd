#!/bin/bash


function_exists() {
    declare -f -F $1 > /dev/null
    return $?
}

function_exists "load_dockerinitd_includes" || {
    load_dockerinitd_includes(){
        . /lib/lsb/init-functions
        DOCKERCOMPOSE_LIBFILE=${DOCKERCOMPOSE_LIBFILE-'/usr/local/src/docker-compose-initd/docker-compose-initd.sh'}
        # script start
        [ -r $DOCKERCOMPOSE_LIBFILE ] || {
            echo 'docker compose libfile not found: '$DOCKERCOMPOSE_LIBFILE
            exit 1
        }
        . $DOCKERCOMPOSE_LIBFILE
    }
}


load_dockerinitd_includes


#####  TEST CONFIGURATION
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
YML_template_PATH=$(echo $DIR'/../composesample')
YML_filename="twoUpOneVolume.yml"
# // config validation has been disabled and will be manually performed here in test
do_validate_config
########

#DESC=${DESC:"docker-compose initd manager"}

# default settings




export PATH=/sbin:/bin:/usr/sbin:/usr/bin

case "$1" in
  start)
        compose_app_start
        exit $?
        ;;
  stop)
        compose_app_stop
        exit $?
        ;;

  reload|force-reload)
        compose_app_reload
        exit $?
        ;;

  restart)
        compose_app_restart
        exit $?
        ;;

  status)
        compose_app_status
        exit $? # notreached due to set -e
        ;;
  *)
        echo "Usage: {start|stop|reload|force-reload|restart|status}"
        exit 1
esac

exit 0
