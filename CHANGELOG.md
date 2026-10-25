# Changelog

## Unreleased

### Changes that may need your action
- The DNS server of dnsmasq is disabled (`port=0`). In DHCP server mode, add `--dhcp-option=option:dns-server,<IP>`,
  otherwise clients get no DNS server. A warning is printed when it is missing. DHCP proxy mode is not affected.
- `domain=example.com` is no longer sent to clients in DHCP server mode. Add `--domain=<domain>` if you need a domain.
- iPXE v2.0.0 is built by default, instead of the master of iPXE at the time of the build.
  Use `--build-arg IPXE_COMMIT=<tag or commit>` to build another version.
- The container exits with the exit code of dnsmasq. It used to exit with 0 even if dnsmasq failed to start.

### Added
- Logs and errors of dnsmasq are written to `docker logs`, including files sent by TFTP.
- A warning when dnsmasq runs as a DHCP server without a DNS server for clients.

### Changed
- The base image is `alpine:3.24` (it was `alpine:3.14`, which is end of life).
- Images are built by GitHub Actions only when a `v*` tag is pushed. Pushing branches no longer publishes images.
- Actions in the workflow are updated to their current major versions.

### Fixed
- `docker stop` stops dnsmasq cleanly. The handler of SIGTERM failed with a TypeError before.
- `docker stop` while the container is preparing no longer starts dnsmasq and waits for the timeout.
- Output of the entrypoint appears in `docker logs` while the container is running.
- README: the names of environment variables, an example of DHCP server mode that failed with
  "junk found in command line", and the ports that are needed.

## v0.2.1
- The last release before this changelog was started.
