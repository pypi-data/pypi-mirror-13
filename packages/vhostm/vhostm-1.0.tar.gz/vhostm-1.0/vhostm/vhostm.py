import argparse
import json
import os
import subprocess
from os import makedirs, remove
from os.path import abspath, join, exists, dirname

from jinja2 import Template

CMDS = ["list", "add", "del", "gen"]

VHOSTM_CONFIG = ".vhostm.conf"

DEFAULT_NGINX_TEMPLATE = """
upstream {{domain}} {
    server {{address}}:{{port}};
}

server {
    listen 80;
    listen [::]:80;
    server_name {{domain}};

    location / {
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;

        proxy_read_timeout  90;

        proxy_pass http://{{domain}};
    }

    {% if static_root %}
    # Media: images, icons, video, audio, HTC
    location ~* \.(?:jpg|jpeg|gif|png|ico|cur|gz|svg|svgz|mp4|ogg|ogv|webm|htc|mst|otf|ttf|woff)$ {
        root {{static_root}};
        # expires 1M;
        access_log off;
        add_header Cache-Control "public";
    }

    # CSS and Javascript
    location ~* \.(?:css|js)$ {
        root {{static_root}};
        # expires 1y;
        access_log off;
        add_header Cache-Control "public";
    }
    {% endif %}
}
"""


class Config(object):
    def __init__(self, vhosts_file, hosts_file,
                 nginx_conf_dir, nginx_template):
        self.vhosts_file = vhosts_file
        self.hosts_file = hosts_file
        self.nginx_conf_dir = nginx_conf_dir
        self.nginx_template = nginx_template

        for d in [dirname(vhosts_file), dirname(hosts_file), nginx_conf_dir]:
            if not exists(d):
                makedirs(d)


class Vhost(object):
    def __init__(self, domain, port, static_root=None, address="127.0.0.1"):
        self.domain = domain
        self.port = port
        self.static_root = static_root
        self.address = address

    def write(self):
        if self.port is None:
            exit("Cannot write vhost without port")

        static_root = self.static_root if self.static_root else ""
        return json.dumps(dict(
            domain=self.domain,
            port=self.port,
            static_root=static_root,
            address=self.address))

    @staticmethod
    def header():
        return "Domain | Address:Port | Static Root"

    @classmethod
    def read(cls, vhost_str):
        vhost = json.loads(vhost_str)
        domain = vhost["domain"]
        port = vhost["port"]
        static_root = vhost["static_root"]
        address = vhost["address"]
        return cls(domain,
                   port,
                   static_root if static_root != "" else None,
                   address)

    def __str__(self):
        return "{} | {}:{} | {}".format(
            self.domain,
            self.address,
            self.port,
            self.static_root if self.static_root else "")

    def __eq__(self, other):
        return self.domain == other.domain


def vhostm_gen(config):
    try:
        with open(config.vhosts_file, "r") as f:
            vhosts = json.load(f)
    except:
        vhosts = {"vhosts": []}

    hosts_file = ""
    try:
        with open(config.hosts_file) as f:
            hosts_file = f.read()
    except FileNotFoundError:
        pass

    hosts = ""
    for vhost_str in vhosts["vhosts"]:
        vhost = Vhost.read(vhost_str)

        hosts += "{}\t{}\n".format(vhost.domain, vhost.address)

        # Write nginx config file
        with open(join(config.nginx_conf_dir, vhost.domain), "w+") as f:
            template = Template(config.nginx_template)
            f.write(template.render(domain=vhost.domain,
                                    port=vhost.port,
                                    address=vhost.address,
                                    static_root=vhost.static_root))

    with open(config.hosts_file, "w+") as f:
        if "#{%block vhostm_hosts%}\n" not in hosts_file:
            hosts_file += "\n#{%block vhostm_hosts%}\n#{%endblock%}\n"

        template = Template(hosts_file)

        def swap_vhostm_hosts(*args, **kwargs):
            yield "\n#{%block vhostm_hosts%}\n" + hosts + "#{%endblock%}\n"

        template.blocks["vhostm_hosts"] = swap_vhostm_hosts
        hosts_file = template.render()
        f.write(hosts_file)

    assert(subprocess.call(["nginx", "-t"]) == 0)

    assert(subprocess.call(["service", "nginx", "reload"]) == 0)


def vhostm_add(config, vhost):
    try:
        with open(config.vhosts_file, "r") as f:
            vhosts = json.load(f)
    except:
        vhosts = {"vhosts": []}

    for vhost_str in vhosts["vhosts"]:
        _vhost = Vhost.read(vhost_str)
        if _vhost == vhost:
            exit("Unable to override existing vhost {}".format(
                vhost.domain))

    vhosts["vhosts"].append(vhost.write())

    with open(config.vhosts_file, "w+") as f:
        json.dump(vhosts, f)

    vhostm_gen(config)


def vhostm_del(config, vhost):
    try:
        with open(config.vhosts_file) as f:
            vhosts = json.load(f)
    except:
        exit("Cannot delete vhost from vhosts_file that does not exist")

    vhosts_dict = {"vhosts": []}
    for vhost_str in vhosts["vhosts"]:
        _vhost = Vhost.read(vhost_str)

        if vhost == _vhost:
            # Remove nginx config file
            remove(join(config.nginx_conf_dir, vhost.domain))
        else:
            vhosts_dict["vhosts"].append(vhost_str)

    with open(config.vhosts_file, "w") as f:
        json.dump(vhosts_dict, f)

    vhostm_gen(config)


def vhostm_list(config):
    try:
        with open(config.vhosts_file) as f:
            vhosts = json.load(f)
    except:
        vhosts = {"vhosts": []}

    print(Vhost.header())
    for vhost_str in vhosts["vhosts"]:
        vhost = Vhost.read(vhost_str)
        if vhost is not None:
            print(vhost)


def get_user_root():
    sudo_user = os.getenv("SUDO_USER")
    user_config = "/home/{}".format(sudo_user)
    if sudo_user == "root":
        user_config = "/root"

    return user_config


def get_args():
    parser = argparse.ArgumentParser()

    hosts_file = "/etc/hosts"
    nginx_conf_dir = "/etc/nginx/sites-enabled"
    vhosts_file = "/etc/vhostm/vhosts.conf"

    nginx_template = DEFAULT_NGINX_TEMPLATE
    nginx_template_file = None

    try:
        user_root = get_user_root()
        with open(abspath(join(user_root, VHOSTM_CONFIG))) as f:
            config = json.load(f)
            hosts_file = config.get("hosts_file",
                                    hosts_file)
            nginx_conf_dir = config.get("nginx_conf_dir",
                                        nginx_conf_dir)
            vhosts_file = config.get("vhosts_file",
                                     vhosts_file)
            nginx_template_file = config.get("nginx_template_file")
    except IOError:
        pass

    cmd_help = ("must supply command. Options are [{}]"
                "").format(", ".join(CMDS))
    parser.add_argument("cmd", help=cmd_help, type=str)

    vhosts_file_help = ("must supply the location of a vhosts_file here or in"
                        "~/.vhostm.conf")
    parser.add_argument("--vhosts_file",
                        help=vhosts_file_help, type=str, default=None)

    vhost_file_help = "the location of a vhost config file"
    parser.add_argument("-f", "--vhost_file",
                        help=vhost_file_help, type=str,
                        default="./.vhost.conf")

    nginx_template_file_help = "the location of the nginx template file"
    parser.add_argument("--nginx_template_file",
                        help=nginx_template_file_help, type=str, default=None)

    hosts_file_help = "the location of the hosts file"
    parser.add_argument("--hosts_file",
                        help=hosts_file_help, type=str, default=None)

    nginx_conf_dir_help = "the nginx configuration directory"
    parser.add_argument("--nginx_conf_dir",
                        help=nginx_conf_dir_help, type=str, default=None)

    domain_help = "the domain to be added or deleted"
    parser.add_argument("-d", "--domain",
                        help=domain_help, type=str)

    port_help = "the port to attach the domain to"
    parser.add_argument("-p", "--port",
                        help=port_help, type=str)

    static_root_help = "the static root to serve files from"
    parser.add_argument("-s", "--static_root",
                        help=static_root_help, type=str, default=None)

    address_help = "the address to forward to (127.0.0.1, 0.0.0.0)"
    parser.add_argument("-a", "--address",
                        help=address_help, type=str, default="127.0.0.1")

    args = parser.parse_args()

    if args.vhosts_file is None:
        args.vhosts_file = vhosts_file

    if args.hosts_file is None:
        args.hosts_file = hosts_file

    if args.nginx_conf_dir is None:
        args.nginx_conf_dir = nginx_conf_dir

    if args.nginx_template_file is None:
        args.nginx_template_file = nginx_template_file

    if args.nginx_template_file is not None:
        with open(abspath(nginx_template_file)) as f:
            nginx_template = f.read()

    setattr(args, "nginx_template", nginx_template)

    if args.static_root:
        args.static_root = abspath(args.static_root)

    return args


def main():
    args = get_args()
    if args.cmd not in CMDS:
        exit("cmd must be one of [{}]".format(", ".join(CMDS)))

    config = Config(abspath(args.vhosts_file),
                    abspath(args.hosts_file),
                    abspath(args.nginx_conf_dir),
                    args.nginx_template)

    cmd_functions = [vhostm_list, vhostm_add, vhostm_del, vhostm_gen]
    for i, cmd in enumerate(CMDS):
        vhost = None
        if args.vhost_file is not None:
            try:
                with open(args.vhost_file) as f:
                    vhost = Vhost.read(f)
            except IOError:
                pass

        if args.domain is not None:
            vhost = Vhost(args.domain,
                          args.port,
                          args.static_root,
                          args.address)

        if args.cmd == cmd:
            kwargs = {}
            if vhost is not None:
                kwargs["vhost"] = vhost
            try:
                cmd_functions[i](config, **kwargs)
            except TypeError as e:
                print(e)
                exit("Missing required arguments to {}".format(cmd))


if __name__ == "__main__":
    main()
