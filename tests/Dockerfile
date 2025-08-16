# syntax=docker/dockerfile:1

FROM python:3.7-slim

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
#------------------------------------------------------------

# This code installs JRE, dockerfile continues after it
# Got it from https://github.com/adoptium/containers
# https://github.com/adoptium/containers/blob/main/24/jre/ubuntu/noble/Dockerfile
# and added minor changes

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="$JAVA_HOME"/bin:"$PATH"

# Default to UTF-8 file.encoding
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN echo Installing JRE; \
    set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        wget \
        # gnupg required to verify the signature
        gnupg \
        # java.lang.UnsatisfiedLinkError: libfontmanager.so: libfreetype.so.6: cannot open shared object file: No such file or directory
        # java.lang.NoClassDefFoundError: Could not initialize class sun.awt.X11FontManager
        # https://github.com/docker-library/openjdk/pull/235#issuecomment-424466077
        fontconfig \
        # utilities for keeping Ubuntu and OpenJDK CA certificates in sync
        # https://github.com/adoptium/containers/issues/293
        ca-certificates p11-kit \
        tzdata \
        # locales ensures proper character encoding and locale-specific behaviors using en_US.UTF-8
        locales \
    ; \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; \
    locale-gen en_US.UTF-8; \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_VERSION=jdk-24.0.2+12

RUN set -eux; \
    ARCH="$(dpkg --print-architecture)"; \
    case "${ARCH}" in \
       amd64) \
         ESUM='bee902852ae8b6698e04eb1599dc94af844ae45b72b3b8ec854350b9aba41335'; \
         BINARY_URL='https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jre_x64_linux_hotspot_24.0.2_12.tar.gz'; \
         ;; \
       arm64) \
         ESUM='6b06ed1d91930ef86afc7d2159948aa9b3054b154cd8afda35d1fddd158fc11d'; \
         BINARY_URL='https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jre_aarch64_linux_hotspot_24.0.2_12.tar.gz'; \
         ;; \
       ppc64el) \
         ESUM='de9ec7034fb369ec9b5d12bba9d51984d14d859006e89ef2b86bbae9bc4c7ae4'; \
         BINARY_URL='https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jre_ppc64le_linux_hotspot_24.0.2_12.tar.gz'; \
         ;; \
       riscv64) \
         ESUM='4a1177077bc5937ec93cfaaff60fd212a8591af241827869c73f87949a1268e9'; \
         BINARY_URL='https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jre_riscv64_linux_hotspot_24.0.2_12.tar.gz'; \
         ;; \
       s390x) \
         ESUM='b25ab757f131f965195fd2cb63853299ed6bef268c845283a5a9fff562840fe2'; \
         BINARY_URL='https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jre_s390x_linux_hotspot_24.0.2_12.tar.gz'; \
         ;; \
       *) \
         echo "Unsupported arch: ${ARCH}"; \
         exit 1; \
         ;; \
    esac; \
    wget --progress=dot:giga -O /tmp/openjdk.tar.gz ${BINARY_URL}; \
    wget --progress=dot:giga -O /tmp/openjdk.tar.gz.sig ${BINARY_URL}.sig; \
    export GNUPGHOME; \
    GNUPGHOME="$(mktemp -d)"; \
    # gpg: key 843C48A565F8F04B: "Adoptium GPG Key (DEB/RPM Signing Key) <temurin-dev@eclipse.org>" imported
    gpg --batch --keyserver keyserver.ubuntu.com --recv-keys 3B04D753C9050D9A5D343F39843C48A565F8F04B; \
    gpg --batch --verify /tmp/openjdk.tar.gz.sig /tmp/openjdk.tar.gz; \
    rm -rf "${GNUPGHOME}" /tmp/openjdk.tar.gz.sig; \
    echo "${ESUM} */tmp/openjdk.tar.gz" | sha256sum -c -; \
    mkdir -p "$JAVA_HOME"; \
    tar --extract \
        --file /tmp/openjdk.tar.gz \
        --directory "$JAVA_HOME" \
        --strip-components 1 \
        --no-same-owner \
    ; \
    rm -f /tmp/openjdk.tar.gz; \
    # https://github.com/docker-library/openjdk/issues/331#issuecomment-498834472
    find "$JAVA_HOME/lib" -name '*.so' -exec dirname '{}' ';' | sort -u > /etc/ld.so.conf.d/docker-openjdk.conf; \
    ldconfig; \
    # https://github.com/docker-library/openjdk/issues/212#issuecomment-420979840
    # https://openjdk.java.net/jeps/341
    java -Xshare:dump;

RUN set -eux; \
    echo "Verifying install ..."; \
    echo "java --version"; java --version && \
    echo "Complete."
#-----------------------------------------------------------------

COPY . /install
WORKDIR /install
RUN pip install --no-cache-dir . && \
    pip install --no-cache-dir \
        pytest \
        pytest-cov \
        numpy \
        jieba \
        tinysegmenter \
        lxml_html_clean \
        konlpy \
        greek-stemmer-pos && \
    python -c "import nltk; nltk.download('punkt')" && \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENTRYPOINT ["pytest"]
