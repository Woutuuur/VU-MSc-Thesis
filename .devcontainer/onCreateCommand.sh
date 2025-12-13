#!/bin/bash

/usr/bin/python3 /data/baristabench/build.py
echo "export GRAALVM_HOME=$(sdk home java 24-graal)" >> ~/.bashrc
sdk install java labsjdk-ce /data/jdk
sdk default java labsjdk-ce
mx -p /workspace/graal/substratevm intellijinit
mx -p /workspace/graal/substratevm build
find /workspace/graal -name mxbuild -print -type d -exec rm -rf {} \;
/workspace/fix-data-dir

exit 0
