FROM ubuntu:22.04

ARG IPXE_COMMIT

RUN apt-get update && \
    apt-get install -y build-essential liblzma-dev isolinux git iproute2 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /pxeboot/config /pxeboot/firmware /pxeboot/os-images && \
    git clone https://github.com/ipxe/ipxe.git && \
    if [ -n "$IPXE_COMMIT" ]; then git -C ipxe checkout -b "$IPXE_COMMIT" "$IPXE_COMMIT"; fi && \
    cd ipxe/src && \
    make bin/ipxe.pxe bin/undionly.kpxe bin/undionly.kkpxe bin/undionly.kkkpxe bin-x86_64-efi/ipxe.efi && \
    cp -v bin/ipxe.pxe bin/undionly.kpxe bin/undionly.kkpxe bin/undionly.kkkpxe bin-x86_64-efi/ipxe.efi /pxeboot/firmware/ && \
    cd ../../ && \
    rm -rf ipxe

FROM alpine:3.14

COPY --from=0 /pxeboot /pxeboot
COPY dnsmasq.conf.j2 /etc/dnsmasq.conf.j2
COPY entrypoint.py /entrypoint.py

RUN apk update && \
    apk add dnsmasq python3 py3-jinja2 iproute2 && \
    rm -rf /var/cache/apk/* && \
    chmod 755 /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
