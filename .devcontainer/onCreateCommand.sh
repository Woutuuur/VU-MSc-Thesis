#!/bin/bash

sdk use java 24-graal
/workspace/fix-data-dir
/usr/bin/python3 /data/baristabench/build.py

sdk install java labsjdk-ce /data/jdk
sdk use java labsjdk-ce
sdk default java labsjdk-ce
mx -p /workspace/graal/substratevm build
mx -p /workspace/graal/substratevm intellijinit

echo "export GRAALVM_HOME=$(sdk home java 24-graal)" >> ~/.bashrc
find /workspace/graal -name mxbuild -print -type d -exec rm -rf {} \;


exit 0
