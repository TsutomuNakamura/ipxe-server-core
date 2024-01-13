#!/usr/bin/env python3
import signal
import os, sys, jinja2, subprocess

class Dnsmasq:
    def __init__(self, script_dir):
        self.script_dir = script_dir

    def create_config(self, interface, ip_ipxe_server, ip_tftp_next_server, ip_http_next_server):
        if os.path.exists('/etc/dnsmasq.conf'):
            # If /etc/dnsmasq.conf already exists, do nothing because it is probably mounted by the user.
            return

        # Create /etc/dnsmasq.conf from a template
        with open(os.path.join(self.script_dir, '/etc/dnsmasq.conf.j2'), 'r') as f:
            template = jinja2.Template(f.read())
            content = template.render({
                "interface": interface,
                "ip_ipxe_server": ip_ipxe_server,
                "ip_tftp_next_server": ip_tftp_next_server,
                "ip_http_next_server": ip_http_next_server
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
        instance.run(dnsmasq_args)

    def __init__(self, dnsmasq_args):
        self.dnsmasq_args = dnsmasq_args

        signal.signal(signal.SIGTERM, Cleanup.run)
        self.dnsmasq_args = dnsmasq_args
        self.ip_tftp_next_server = os.environ.get('IP_TFTP_NEXT_SERVER')
        self.ip_http_next_server = os.environ.get('IP_HTTP_NEXT_SERVER')
        self.prepare(self.ip_tftp_next_server, self.ip_http_next_server)

    def usage(self):
        print("Usage: %s [options]" % sys.argv[0])
        print("Options:")
        print("  -h, --help\t\t\tShow this help message and exit")
        sys.exit(1)

    def prepare(self, ip_tftp_next_server, ip_http_next_server):
        # Create /etc/dnsmasq.conf
        interface       = Network.get_interface()
        ip_ipxe_server  = Network.get_ip(interface)

        if ip_tftp_next_server is None:
            print("IP_TFTP_NEXT_SERVER is not specified. IP of this node " + ip_ipxe_server + " will be used.")
            ip_tftp_next_server = ip_ipxe_server

        if ip_http_next_server is None:
            print("IP_HTTP_NEXT_SERVER is not specified. IP of this node " + ip_ipxe_server + " will be used.")
            ip_http_next_server = ip_ipxe_server

        if self.verify_to_use_default_dhcp_range():
            # If the user did not specify a DHCP range, use the dnsmasq as proxy mode.
            self.dnsmasq_args.append("--dhcp-range=" + ip_ipxe_server + ",proxy")

        print("interface: " + interface + ", ip_tftp_next_server: " + ip_tftp_next_server
              + ", ip_http_next_server: " + ip_http_next_server + ", ip_ipxe_server: " + ip_ipxe_server
              + ", args: " + str(self.dnsmasq_args))

        self.dnsmasq.create_config(interface, ip_ipxe_server, ip_tftp_next_server, ip_http_next_server)

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

