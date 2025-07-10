FROM mcr.microsoft.com/devcontainers/base:bookworm

ARG MX_BRANCH
ARG DACAPO_VERSION

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y git \
    generate-ninja ninja-build \
    python3 python3-venv python3-pip \
    maven \
    gdb \
    libxrender1 libxtst6 libxi6 libgtk-3-0 \
    wrk

RUN apt-get clean all

RUN mkdir -p /data
RUN chown -R vscode:vscode /data
RUN chmod -R 777 /data

ENV MX_PATH=/data/mx \
    JAVA_HOME=/data/jdk \
    PATH="/data/mx/:$PATH"

# Get the mx tool
RUN git clone -b ${MX_BRANCH} --depth 1 https://github.com/graalvm/mx.git ${MX_PATH}

# mx needs to be able to write files to its own directory
RUN chmod -R 777 /data/mx

# Copy graal project files temporarily for setup
COPY graal/.mx_vcs_root /tmp/graal/.mx_vcs_root
COPY graal/common.json /tmp/graal/common.json
COPY graal/ci.jsonnet /tmp/graal/ci.jsonnet
COPY graal/.git /tmp/graal/.git

# Fetch the JDK
RUN ${MX_PATH}/mx -p /tmp/graal --java-home= fetch-jdk --jdk-id labsjdk-ce-latest --to /data/jdk-dl --alias ${JAVA_HOME}

# Create some shorthands for mx commands
RUN echo "alias aot='mx -p /workspace/graal/substratevm native-image'" >> /etc/bash.bashrc && \
    echo "alias vm='mx -p /workspace/graal/compiler vm'" >> /etc/bash.bashrc && \
    echo "alias build-aot='mx -p /workspace/graal/substratevm build'" >> /etc/bash.bashrc && \
    echo "alias build-jvm='mx -p /workspace/graal/compiler build'" >> /etc/bash.bashrc && \
    echo "alias igv='mx --java-home /usr/local/sdkman/candidates/java/21.0.7-graal/ -p /workspace/graal/compiler/ igv'" >> /etc/bash.bashrc

RUN wget -q -O /tmp/dacapobench.zip https://download.dacapobench.org/chopin/dacapo-${DACAPO_VERSION}.zip 
RUN mkdir /data/dacapobench
RUN unzip /tmp/dacapobench.zip -d /data/dacapobench
COPY native-image-run /data/dacapobench/native-image-run

RUN wget -q -O /tmp/jmc.tar.gz https://github.com/adoptium/jmc-build/releases/download/8.3.0/org.openjdk.jmc-8.3.0-linux.gtk.x86_64.tar.gz
RUN mkdir /data/jmc
RUN tar -xzf /tmp/jmc.tar.gz -C /data/jmc --strip-components=1

# Allow full access to dacapo benchmarks
RUN chmod -R 777 /data/dacapobench

# Clone barista benchmarks & tooling
RUN git clone https://github.com/barista-benchmarks/barista.git /data/baristabench
RUN chmod -R 777 /data/baristabench
RUN chown -R vscode:vscode /data/baristabench
RUN git clone https://github.com/giltene/wrk2.git /tmp/wrk2
RUN cd /tmp/wrk2 && make && cp wrk /usr/bin/wrk2

# Cleanup
RUN rm -rf /tmp/*

ENV BASH_ENV="/usr/local/sdkman/bin/sdkman-init.sh"
ENV DISPLAY=:0
ENTRYPOINT ["/bin/bash", "-c"]
