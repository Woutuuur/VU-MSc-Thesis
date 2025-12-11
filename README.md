# Profile-Guided Optimizations in AOT Java compilation

WIP

## Structure

WIP

## Setup

First, clone the repo and enter the directory:

```bash
git clone https://github.com/Woutuuur/VU-MSc-Thesis --recursive --shallow-submodules aot-pgo
cd aot-pgo
```

There are two main methods to continue the setup.

**Method 1: devcontainer (recommended)**

This project has a devcontainer configuration provided in [.devcontainer/](.devcontainer). [Devcontainers](https://containers.dev/) are reproducible development containers for individual projects. Build and start the devcontainer using a supporting IDE/editor (e.g. vscode, JetBrains IDEs or Toolbox, etc.) or using a dedicated tool such as [DevPod](https://devpod.sh/) (my recommendation) by selecting the cloned directory. Wait a couple minutes for the devcontainer to download and setup all the required benchmarks, tooling, languages, etc., and you're done. This setup ensures the setup is identical regardless of host environment. There are no prerequisites besides Docker.

A few caveats:

- The  [devcontainer.json](.devcontainer/devcontainer.json#L27) specifies X-forwarding for graphical application support (used for Graal's graph viewer called IGV). This has only been tested on a Linux host operating system and may not work on others.
-  The [devcontainer.json](.devcontainer/devcontainer.json#L20-L23) furthermore specifies SELinux security flags. It is not clear whether these flags hinder the build process of a devcontainer on a non-SELinux system but you can remove them if so.

**Method 2: manual**

We will not go into too much detail here, because this project was developed with a devcontainer setup in mind. A (very) coarse-grained guide:

1. To setup the project manually, much of the installation will be similar to the installation steps performed by the devcontainer build process in its [Dockerfile](.devcontainer/Dockerfile), so use this as a reference to create a similar setup locally. When setting up the `mx` tooling, checkout the `release/graal-vm/24.2` branch. For DaCapo, use version `23.11-MR2-chopin`.
1. After setting up the equivalent of the Dockerfile, install [SDKMAN!](https://sdkman.io/) and use it to install the following Java versions: `24-graal`, `21.0.7-graal`, `24-graalce`.
1. Lastly, follow the steps in [onCreateCommand.sh](.devcontainer/onCreateCommand.sh).

## Usage

WIP 
