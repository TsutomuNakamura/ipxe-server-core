# ipxe-server-core
This is a core docker image for iPXE server.
This docker image only has a feature of iPXE not a server that provide any OS images to boot and install(`next-server`).
This docker image requires preparing `next-server` on your own or build it that is based this image if you want to install OS or boot an OS.

## Building
```
docker built -t tsutomu/ipxe-server-core .
```

