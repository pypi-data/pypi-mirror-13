import requests, os, time, argh, subprocess
from jinja2 import StrictUndefined
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader


METADATA_HOST_VAR = os.environ.get("METADATA_HOST_VAR", None)
METADATA_PORT_VAR = os.environ.get("METADATA_PORT_VAR", None)

METADATA_HOST = os.environ.get(METADATA_HOST_VAR, "169.254.169.254")
METADATA_PORT = os.environ.get(METADATA_PORT_VAR, "80")


def get_ec2_metadata(path):
    response = requests.get("http://{}:{}/latest/{}".format(METADATA_HOST, METADATA_PORT, path))
    return response.json()


def write_updated_config(template, role):
    iam = get_ec2_metadata("meta-data/iam/security-credentials/" + role)
    context = dict(iam=iam, environ=dict(os.environ))

    dir_name = os.path.dirname(template)
    base_name = os.path.basename(template)

    environment = Environment(loader=FileSystemLoader(dir_name),
                              undefined=StrictUndefined)

    out_path = dir_name + "/" + base_name[:-len(".j2")]
    tmpl = environment.get_template(base_name)

    with open(out_path, "w") as out:
        out.write(tmpl.render(**context))


def go(template, check_command, reload_command, interval_seconds=60 * 60):
    role = os.environ["IAM_ROLE"]

    write_updated_config(template, role)

    pid = os.fork()

    if pid == 0:
        while True:
            time.sleep(interval_seconds)
            write_updated_config(template, role)
            print check_command
            if subprocess.call(check_command.split()) == 0:
                print reload_command
                subprocess.call(reload_command.split())


def main():
    argh.dispatch_command(go)

