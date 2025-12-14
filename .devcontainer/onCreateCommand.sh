#!/bin/bash

sdk use java 24-graal
/usr/bin/python3 /data/baristabench/build.py

sdk install java labsjdk-ce /data/jdk
sdk use java labsjdk-ce
sdk default java labsjdk-ce

# Clean up any existing mxbuild directories to create a clean devcontainer setup
find /workspace/graal -name mxbuild -print -type d -exec rm -rf {} \;

mx -p /workspace/graal/substratevm build
mx -p /workspace/graal/substratevm intellijinit

echo "export GRAALVM_HOME=$(sdk home java 24-graal)" >> ~/.bashrc
/workspace/fix-data-dir

exit 0
