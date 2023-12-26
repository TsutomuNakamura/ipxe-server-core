#!/usr/bin/env python3

import os, sys
import jinja2

class IPXE:
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Get an instance of the Dnsmasq
    self.dnsmasq = Dnsmasq()

    @staticmethod
    def main(dnsmasq_args):
        instance = IPXE()
        instance.run(dnsmasq_args)

    def __init__(self):
        pass

    def usage(self):
        print("Usage: %s [options]" % sys.argv[0])
        print("Options:")
        print("  -h, --help\t\t\tShow this help message and exit")
        sys.exit(1)

    def prepare(self, ipxe_server_ip, next_server_ip):
        # Create /etc/dnsmasq.conf
        self.dnsmasq.create_config(ipxe_server_ip, next_server_ip)

    def run(self):
        # Run dnsmasq process
        subprocess.run(["dnsmasq", "--keep-in-foreground", "--user", "dnsmasq" "--conf-dir", "/etc/dnsmasq.d"])


class Dnsmasq:

    def create_config(self, ipxe_server_ip, next_server_ip):
        # Create /etc/dnsmasq.conf from a template
        with open(os.path.join(self.script_dir, 'dnsmasq.conf.j2'), 'r') as f:
            template = jinja2.Template(f.read())
            content = template.render({"ipxe_server_ip": ipxe_server_ip, "next_server_ip": next_server_ip})

        with open('/etc/dnsmasq.conf', 'w') as f:
            f.write(content)

if __name__ == '__main__':
    IPXE().main(sys.argv[1:])

