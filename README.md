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

## Running ipxe-server-core on a macvlan network
First, you have to create a macvlan network that belonging in the network that your host and iPXE client in.
```
docker network create -d macvlan --subnet 172.31.0.0/16 --ip-range=172.31.127.0/24 --gateway=172.31.0.1 -o parent=enp1s0 macvlan_ipxe
```

Run a container on the macvlan that you just previously created.
```
docker run --rm --privileged --net=macvlan_ipxe -ti tsutomu/ipxe-server-core
```

## Building
```
docker built -t tsutomu/ipxe-server-core .
```

