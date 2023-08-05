import os
import sys
import posixpath
import json
import time
# import glob
import serial
import serial_list

import click
import requests

# from serial_list
# api_prefix = "http://192.168.21.48:8080"
# api_prefix = "https://iot.seeed.cc"
login_endpoint = "/v1/user/login"
node_list_endpoint = "/v1/nodes/list"
well_known_endpoint = "/v1/node/.well-known"
nodes_create_endpoint = "/v1/nodes/create"
nodes_rename_endpoint = "/v1/nodes/rename"


class Wio(object):

    def __init__(self):
        # self.home = home
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        # cur_dir = os.path.split(os.path.realpath(__file__))[0]
        cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
        db_file_path = '%s/config.json' % cur_dir
        open("%s/config.json"%cur_dir,"w").write(json.dumps(self.config))
        if self.verbose:
            click.echo('config[%s] = %s' % (key, value), file=sys.stderr)

    def __repr__(self):
        return '<Wio %r>' % self.home


pass_wio = click.make_pass_decorator(Wio, ensure=True)


@click.group()
# @click.option('--wio-home', envvar='REPO_HOME', default='.wio',
#               metavar='PATH', help='Changes the wiository folder location.')
# @click.option('--config', nargs=2, multiple=True,
#               metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode.')
@click.version_option('0.0.8')
@click.pass_context
def cli(ctx, verbose):
    """Wio is a command line tool that showcases how to build complex
    command line interfaces with Click.

    This tool is supposed to look like a distributed version control
    system to show how something like this can be structured.
    """
    # Create a wio object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_wio decorator.
    ctx.obj = Wio()
    ctx.obj.verbose = verbose
    # config.json
    # cur_dir = os.path.split(os.path.realpath(__file__))[0]
    cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
    if not os.path.exists(cur_dir):
        text = {"email":"", "token":""}
        os.mkdir(cur_dir)
        open("%s/config.json"%cur_dir,"w").write(json.dumps(text))
    db_file_path = '%s/config.json' % cur_dir
    config = json.load(open(db_file_path))
    ctx.obj.config = config

def login_server(ctx, param, value):
    # print pass_wio.config
    wio = ctx.obj
    config = wio.config
    mserver = config.get("mserver", None)
    if mserver:
        click.echo("Current mserver is: %s" %mserver)
        return

    # print "prompt input"
    while True:
        click.echo("  1. International[https://iot.seeed.cc]")
        click.echo("  2. China[https://cn.iot.seeed.cc]")
        click.echo("  3. Customer")
        server = raw_input("choice main server:")
        if server == "1":
            wio.set_config("mserver","https://iot.seeed.cc")
            return
        elif server == "2":
            wio.set_config("mserver","https://cn.iot.seeed.cc")
            return
        elif server == "3":
            break
        else:
            continue

    server_ip = raw_input("Input main server ip:")
    wio.set_config("mserver", "http://%s:8080" %server_ip)
    wio.set_config("mserver_ip", server_ip)

@cli.command()
@click.option('--mserver', callback=login_server, expose_value=False, help='The developer\'s email address', is_eager=True)
@click.option('--email', prompt='email', help='The developer\'s email address')
@click.option('--password', prompt='password', hide_input=True, help='The login password.',)
@pass_wio
def login(wio, email, password):
    '''login with your wio link account'''
    params = {"email":email, "password":password}
    api_prefix = wio.config.get("mserver", None)
    r = requests.post("%s%s" %(api_prefix, login_endpoint), params=params)
    token = r.json().get("token", None)
    wio.set_config('email', email)
    wio.set_config('token', token)
    if token:
        click.echo("login success!")
    else:
        error = r.json().get("error", None)
        if not error:
            error = r.json().get("msg", None)
        click.echo(error)

@cli.command()
@pass_wio
def list(wio):
    '''List WioLinks and API'''
    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo("Please login [wio login]")
        return
    params = {"access_token":token}
    r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params)
    json_response = r.json()

    # click.echo(json_response)
    for n in json_response["nodes"]:
        if n["online"]:
            onoff = "online"
        else:
            onoff = "offline"
        click.echo("  wiolink[%s], token[%s] is %s" %(n["name"], n["node_key"], onoff))
        if n["online"]:
            # click.echo("  API:")
            params = {"access_token":n["node_key"]}
            # click.echo("%s%s" %(api_prefix, well_known_endpoint))
            r = requests.get("%s%s" %(api_prefix, well_known_endpoint), params=params)
            well_response = r.json()
            # click.echo(well_response)
            well_known = well_response["well_known"]
            for api in well_known:
                click.echo("    " + api)
            click.echo()
    click.echo()

@cli.command()
@click.argument('token')
@click.argument('method')
@click.argument('endpoint')
@click.option('--xchange', help='xchange server url')
@pass_wio
def call(wio, method, endpoint, token, xchange):
    '''
    request api test, return json.
    example: wio call 98dd464bd268d4dc4cb9b37e4e779313 GET /v1/node/GroveTempHumProD0/temperature
    '''
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix:
        click.echo("Please login [wio login]")
        return
    api = "%s%s?access_token=%s" %(api_prefix, endpoint, token)
    # print api
    if method == "GET":
        r = requests.get(api)
    elif method == "POST":
        r = requests.post(api)
    else:
        click.echo("API method [%s] is wrong, should be GET or POST." %method)
        return
    try:
        click.echo(r.json())
    except Exception as e:
        click.echo("Error[%s], API[%s]" %(e, api))

@cli.command()
@pass_wio
def state(wio):
    '''login state'''
    email = wio.config.get("email",None)
    mserver = wio.config.get("mserver",None)
    token = wio.config.get("token",None)
    click.echo("email: %s" %email)
    click.echo("token: %s" %token)
    click.echo("mserver: %s" %mserver)

@cli.command()
@click.argument('subcommand')
# @click.argument('sdf')
# @click.option('--mserver', default= None, help='Set main server ip, such as 192.168.21.48')
@pass_wio
def set(wio, subcommand):
    '''
    subcommand: mserver
    '''
    if subcommand == "mserver":
        while True:
            click.echo("  1. International[https://iot.seeed.cc]")
            click.echo("  2. China[https://cn.iot.seeed.cc]")
            click.echo("  3. Customer")
            server = raw_input("choice main server:")
            if server == "1":
                wio.set_config("mserver","https://iot.seeed.cc")
                wio.set_config("mserver_ip","45.79.4.239")
                return
            elif server == "2":
                wio.set_config("mserver","https://cn.iot.seeed.cc")
                wio.set_config("mserver_ip","120.25.216.117")
                return
            elif server == "3":
                break
            else:
                continue

        server_ip = raw_input("Input main server ip:")
        wio.set_config("mserver", "http://%s:8080" %server_ip)
        wio.set_config("mserver_ip", server_ip)


@cli.command()
@pass_wio
def setup(wio):
    click.echo("TIP:1. main server can connect. 2. plug usb connect!")
    if not click.confirm('Do you want to continue?', default=True):
        click.echo('Quit setup!')

    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo("Please login [wio login]")
        return
    params = {"name":"node000","access_token":token}
    r = requests.post("%s%s" %(api_prefix, nodes_create_endpoint), params=params)
    json_response = r.json()

    node_key = json_response["node_key"]
    node_sn = json_response["node_sn"]

    # list serial
    ports = serial_list.serial_ports()
    # click.echo(ports)
    # if serial <= 1, =0
    count = len(ports)
    if count == 0:
        pass #scan
    elif count == 1:
        pass
        port = ports[0]
    elif count >= 2:
        for x in range(len(ports)):
            click.echo("[%s]: %s" %(x, ports[x]))
            # multiple serial
        value = click.prompt('Please choice a device', type=int)
        port = ports[x]

    click.echo("conncet to %s" %port)
    click.echo("TIP:1. device must on config mode!")
    if not click.confirm('Do you want to continue?', default=True):
        click.echo('Quit setup!')

    # if click.confirm('Do you want change your exchange server?', default=False):
    #     xchange_ip = click.prompt('Please enter exchange server ip', type=str) #customer type?
    #     xchange_ep = click.prompt('Please enter exchange server endpoint', type=destr) #customer type?

    ap = click.prompt('Please enter a AP name', type=str)
    ap_pwd = click.prompt('Please enter AP password', type=str)
    d_name = click.prompt('Please enter device name', type=str)

    # display all info
    msvr = wio.config.get("mserver", None)
    click.echo("main server: %s" %msvr)
    # click.echo("xchange server ip: msvr_ip")
    # click.echo("xchange server endpoint:")
    click.echo("ap name: %s" %ap)
    click.echo("ap password: %s" %ap_pwd)
    click.echo("device name: %s" %d_name)

    if not click.confirm('Do you confirm setup info?', default=True):
        pass #again?

    # send serial command
    msvr_ip = wio.config.get("mserver_ip", None)
    xsvr_ip = msvr_ip
    with serial.Serial(port, 115200, timeout=10) as ser:
        cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, msvr_ip, xsvr_ip)
        click.echo(cmd)
        ser.write(cmd.encode('utf-8'))
        # while True:
        if "ok" in ser.readline():
            click.echo("wifi info write success.")

    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo("Please login [wio login]")
        return

    # click.echo(json_response)
    state_online = False
    for i in range(30):
        params = {"access_token":token}
        r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params)
        json_response = r.json()
        for n in json_response["nodes"]:
            if n["node_sn"] == node_sn and n["online"]:
                click.echo("device connect server success.")
                state_online = True
                break
        if state_online:
            break
        time.sleep(1)

    if not state_online:
        click.echo("device connect server failure.")
        return

    params = {"name":d_name,"node_sn":node_sn,"access_token":token}
    r = requests.post("%s%s" %(api_prefix, nodes_rename_endpoint), params=params)
    json_response = r.json()
    click.echo(json_response)
    if json_response.get("result", None) == "ok":
        click.echo("device set name success.")
    else:
        click.echo("device set name failure.")
        return

    click.echo("wio setup complete.")

# def serial_ports():
#     """ Lists serial port names
#
#         :raises EnvironmentError:
#             On unsupported or unknown platforms
#         :returns:
#             A list of the serial ports available on the system
#     """
#     if sys.platform.startswith('win'):
#         ports = ['COM%s' % (i + 1) for i in range(256)]
#     elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
#         # this excludes your current terminal "/dev/tty"
#         ports = glob.glob('/dev/tty[A-Za-z]*')
#     elif sys.platform.startswith('darwin'):
#         ports = glob.glob('/dev/tty.*')
#     else:
#         raise EnvironmentError('Unsupported platform')
#
#     result = []
#     for port in ports:
#         try:
#             s = serial.Serial(port)
#             s.close()
#             result.append(port)
#         except (OSError, serial.SerialException):
#             pass
#     return result

# @cli.command()
# @click.option('--hash-type', '-h', 'type',  prompt='123', type=click.Choice(['md5', 'sha1']))
# def hello(type):
#     click.echo(type)
#     choices = ["12", "123"]
#     click.Choice(choices)
#     value = click.prompt('Please enter a valid integer', type=int)
#     if click.confirm('Do you want to continue?'):
#         click.echo('Well done!')


# @cli.command()
# @click.argument('src')
# @click.argument('dest', required=False)
# @click.option('--shallow/--deep', default=False,
#               help='Makes a checkout shallow or deep.  Deep by default.')
# @click.option('--rev', '-r', default='HEAD',
#               help='Clone a specific revision instead of HEAD.')
# @pass_wio
# def clone(wio, src, dest, shallow, rev):
#     """Clones a wiository.
#
#     This will clone the wiository at SRC into the folder DEST.  If DEST
#     is not provided this will automatically use the last path component
#     of SRC and create that folder.
#     """
#     if dest is None:
#         dest = posixpath.split(src)[-1] or '.'
#     click.echo('Cloning wio %s to %s' % (src, os.path.abspath(dest)))
#     wio.home = dest
#     if shallow:
#         click.echo('Making shallow checkout')
#     click.echo('Checking out revision %s' % rev)
#
#
# @cli.command()
# @click.confirmation_option()
# @pass_wio
# def delete(wio):
#     """Deletes a wiository.
#
#     This will throw away the current wiository.
#     """
#     click.echo('Destroying wio %s' % wio.home)
#     click.echo('Deleted!')
#
#
# @cli.command()
# @click.option('--username', prompt=True,
#               help='The developer\'s shown username.')
# @click.option('--email', prompt='E-Mail',
#               help='The developer\'s email address')
# @click.password_option(help='The login password.')
# @pass_wio
# def setuser(wio, username, email, password):
#     """Sets the user credentials.
#
#     This will override the current user config.
#     """
#     wio.set_config('username', username)
#     wio.set_config('email', email)
#     wio.set_config('password', '*' * len(password))
#     click.echo('Changed credentials.')
#
#
# @cli.command()
# @click.option('--message', '-m', multiple=True,
#               help='The commit message.  If provided multiple times each '
#               'argument gets converted into a new line.')
# @click.argument('files', nargs=-1, type=click.Path())
# @pass_wio
# def commit(wio, files, message):
#     """Commits outstanding changes.
#
#     Commit changes to the given files into the wiository.  You will need to
#     "wio push" to push up your changes to other wiositories.
#
#     If a list of files is omitted, all changes wiorted by "wio status"
#     will be committed.
#     """
#     if not message:
#         marker = '# Files to be committed:'
#         hint = ['', '', marker, '#']
#         for file in files:
#             hint.append('#   U %s' % file)
#         message = click.edit('\n'.join(hint))
#         if message is None:
#             click.echo('Aborted!')
#             return
#         msg = message.split(marker)[0].rstrip()
#         if not msg:
#             click.echo('Aborted! Empty commit message')
#             return
#     else:
#         msg = '\n'.join(message)
#     click.echo('Files to be committed: %s' % (files,))
#     click.echo('Commit message:\n' + msg)
#
#
# @cli.command(short_help='Copies files.')
# @click.option('--force', is_flag=True,
#               help='forcibly copy over an existing managed file')
# @click.argument('src', nargs=-1, type=click.Path())
# @click.argument('dst', type=click.Path())
# @pass_wio
# def copy(wio, src, dst, force):
#     """Copies one or multiple files to a new location.  This copies all
#     files from SRC to DST.
#     """
#     for fn in src:
#         click.echo('Copy from %s -> %s' % (fn, dst))
