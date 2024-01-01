#!/usr/bin/env python3
import signal
import os, sys, jinja2, subprocess

class Dnsmasq:
    def __init__(self, script_dir):
        self.script_dir = script_dir

    def create_config(self, interface, ipxe_server_ip, next_server_ip, use_default_dhcp_range):
        if os.path.exists('/etc/dnsmasq.conf'):
            # If /etc/dnsmasq.conf already exists, do nothing because it is probably mounted by the user.
            return

        # Create /etc/dnsmasq.conf from a template
        with open(os.path.join(self.script_dir, '/etc/dnsmasq.conf.j2'), 'r') as f:
            template = jinja2.Template(f.read())
            content = template.render({
                "interface": interface,
                "ipxe_server_ip": ipxe_server_ip,
                "next_server_ip": next_server_ip,
                "use_default_dhcp_range": use_default_dhcp_range
            })

        with open('/etc/dnsmasq.conf', 'w') as f:
            print(content)
            f.write(content)


class Network:
    @staticmethod
    def get_interface():
        # Get the interface name
        return subprocess.check_output(["ip", "rout"]).decode("utf-8").split("dev ")[1].split(" ")[0]

    @staticmethod
    def get_ip(interface):
        # Get the IP address of the interface
        return subprocess.check_output(["ip", "addr", "show", interface]).decode("utf-8").split("inet ")[1].split("/")[0]


class Cleanup:
    @staticmethod
    def run():
        # Stop dnsmasq process
        print("Stopping dnsmasq.")
        subprocess.run(["pkill", "dnsmasq"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

class IPXE:
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Get an instance of the Dnsmasq
    dnsmasq = Dnsmasq(script_dir)

    @staticmethod
    def main(dnsmasq_args):
        instance = IPXE(dnsmasq_args)
        instance.prepare(instance.next_server_ip)
        instance.run(dnsmasq_args)

    def __init__(self, dnsmasq_args):
        signal.signal(signal.SIGTERM, Cleanup.run)
        self.dnsmasq_args = dnsmasq_args
        self.next_server_ip = os.environ.get('NEXT_SERVER_IP')

    def usage(self):
        print("Usage: %s [options]" % sys.argv[0])
        print("Options:")
        print("  -h, --help\t\t\tShow this help message and exit")
        sys.exit(1)

    def prepare(self, next_server_ip=None):
        # Create /etc/dnsmasq.conf
        interface       = Network.get_interface()
        ipxe_server_ip  = Network.get_ip(interface)

        # If next_server_ip is not specified, use ipxe_server_ip. It requires that the DHCP server is running on the same host as the iPXE server.
        if next_server_ip is None:
            next_server_ip = ipxe_server_ip

        use_default_dhcp_range = self.verify_to_use_default_dhcp_range()

        print("interface: " + interface + ", ipxe_server_ip: " 
              + ipxe_server_ip + ", next_server_ip: " + next_server_ip 
              + ", use_default_dhcp_range: " + str(use_default_dhcp_range))

        self.dnsmasq.create_config(interface, ipxe_server_ip, next_server_ip, use_default_dhcp_range)

    def verify_to_use_default_dhcp_range(self):
        # Check if the user specified the DHCP range
        for arg in self.dnsmasq_args:
            if arg.startswith("--dhcp-range"):
                return False
        return True

    def run(self, dnsmasq_args):
        # Run dnsmasq process
        print("Starting dnsmasq. (dnsmasq --keep-in-foreground --conf-dir /etc/dnsmasq.d " + " ".join(dnsmasq_args) + ")")
        subprocess.run(["dnsmasq", "--keep-in-foreground", "--conf-dir", "/etc/dnsmasq.d"] + dnsmasq_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

if __name__ == '__main__':
    IPXE.main(sys.argv[1:])

