"""
Copyright: 2016 Saito Tsutomu
License: Python Software Foundation License
"""
import paramiko, os, re, sys, time, yaml
import digitalocean as do

class _Setting(yaml.YAMLObject):
    yaml_tag = '!Setting'

class _Manager(do.Manager):
    def __init__(self):
        fnam = 'dioc.yml'
        if not os.path.exists(fnam):
            sys.stderr.write('%s not found\n' % fnam)
            return
        with open(fnam) as fp:
            y = yaml.load(fp)
            self.__dict__.update(y.__dict__)
        super().__init__(token=self.token)

def ssh_key_id(name=None):
    if not name:
        name = _manager.default_sshkey
    for sk in _manager.get_all_sshkeys():
        if sk.name == name:
            return sk.id
    return None

def image_id(name, private=False):
    for im in _manager.get_images(private):
        if im.name == name:
            return im.id

def droplet_id(name):
    for dr in _manager.get_all_droplets():
        if dr.name == name:
            return dr.id

def droplet(name):
    id = droplet_id(name)
    return _manager.get_droplet(id)

def Droplet(name, image=None, size=None, region=None,
            ssh_keys=None, no_create=False):
    if not image:
        image = _manager.get_image('coreos-stable').id
    else:
        image = image_id(image)
    dc = {'name': name, 'image': image}
    if not size:
        size = _manager.default_size
    if not region:
        region = _manager.default_region
    if not ssh_keys:
        ssh_keys = [ssh_key_id()]
    if size:
        dc['size'] = size
    if region:
        dc['region'] = region
    if ssh_keys:
        dc['ssh_keys'] = ssh_keys
    dr = do.Droplet(token=_manager.token, **dc)
    if not no_create:
        try:
            dr.create()  
        except Exception as e:
            sys.stderr.write('%s\n' % e)
            return None
        dr.get_action(dr.action_ids[0]).wait()
        dr.load()
    return dr

def ssh_host(name):
    d = droplet(name)
    return '%s@%s' % (ssh_user(d), d.ip_address)

def ssh_file(file):
    m = re.match('(.*)(:.*)|(.*)', file)
    if not m:
        return file
    h, f1, f2 = m.groups()
    return ssh_host(h) + f1 if h else f2

def ssh_user(dr):
    return 'core' if dr.image['distribution'] == 'CoreOS' else 'root'

def ssh_client(dr, user=None):
    if not user:
        user = ssh_user(dr)
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ip = dr.ip_address
    for i in range(6):
        try:
            time.sleep(1)
            cli.connect(ip, username=user)
            return cli
        except:
            pass
    else:
        sys.stderr.write('paramiko.connect error\n')

_manager = _Manager()


