#!/bin/bash
set -xe

export SLAVES_COUNT=2
export DEPLOY_TIMEOUT=180
export TEST_SCRIPT="/usr/bin/python /vagrant/solar-resources/examples/hosts_file/hosts.py"

./utils/jenkins/run.sh
