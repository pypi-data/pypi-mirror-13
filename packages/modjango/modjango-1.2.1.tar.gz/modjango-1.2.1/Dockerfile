from phusion/baseimage:latest

run apt-get update
run apt-get upgrade -y
run apt-get install python3-dev -y
run apt-get install python3-pip -y
run apt-get install python3-pep8 python3-coverage -y
run apt-get install mercurial -y

add / /python_project

run cd /python_project && python3 setup.py install

run chmod +x /python_project/test.sh


volume /python_project

ENV MONGO_URI=mongodb://mongodb
ENV MONGO_REPLICA_SET_NAME=

entrypoint ["/python_project/test.sh"]
