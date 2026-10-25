# ipxe-server-core
This is a core docker image for iPXE server.
This docker image only has a feature of iPXE not a server that provide any OS images to boot and install(`next-server`).
This docker image requires preparing `next-server` on your own or build it that is based this image if you want to install OS or boot an OS.

## Run a container
This image requires network drivers `host` or `macvlan` that is belonging in the same network with iPXE client.

## Running ipxe-server-core on a host network
An example to run ipxe-server-core on your host network is like below.
This way requires the host to be able to use ports 53(DNS), 67(DHCP), 68(DHCP), 69(TFTP).

```
docker run --rm --privileged --net=host -ti tsutomu/ipxe-server-core
```

`ipxe-server-core` will launch as a DHCP proxy mode if you start it without any argumments.
This means that you should prepare another DHCP that provide IP addresses to clients.

## Running ipxe-server-core on a macvlan network
First, you have to create a macvlan network that belonging in your host and iPXE client.
And run a container with privileged mode on the network.
```
docker network create -d macvlan --subnet=172.31.0.0/16 --ip-range=172.31.127.0/24 --gateway=172.31.0.1 -o parent=enp1s0 macvlan_ipxe
docker run --rm --privileged --net=macvlan_ipxe -ti tsutomu/ipxe-server-core
```

## Run as a DHCP server or as a DHCP proxy mode
You can launch `ipxe-server-core` as a DHCP server or DHCP proxy mode.
You have to launch it as a DHCP proxy mode if you already have another DHCP server in your network.

### DHCP server mode
```
docker run --rm --privileged --net=macvlan_ipxe \
    -ti tsutomu/ipxe-server-core -- \
    --dhcp-range=172.31.0.201,172.31.0.250,255.255.0.0 \
    --dhcp-option=option:router,172.31.0.1 \
    --dhcp-option=option:dns-server,8.8.8.8
```

### DHCP proxy mode
```
docker run --rm --privileged --net=macvlan_ipxe -e IP_TFTP_NEXT_SERVER=x.x.x.x -e IP_HTTP_NEXT_SERVER=y.y.y.y -ti tsutomu/ipxe-server-core
```

`IP_TFTP_NEXT_SERVER` is an IP address of the server that provide iPXE firmware with TFTP.
`IP_HTTP_NEXT_SERVER` is an IP address of the server that provide iPXE script and images.
If either of them is not specified, the IP of the ipxe-server-core container will be used.

## Logs
Logs of dnsmasq, including errors and files sent by TFTP, are written to `docker logs`.

```
docker logs ipxe-server-core
```

If you want to see details of each DHCP request, add `--log-dhcp` to the arguments.
If you want to write logs to a file instead, add `--log-facility=<path to a file>`.

The container exits with the exit code of dnsmasq.
For example, the exit code will be non-zero if dnsmasq failed to start because a port is already in use.

## Building an image
```
docker build -t tsutomu/ipxe-server-core .
```

