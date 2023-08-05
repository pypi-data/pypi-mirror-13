"""
Copyright: 2016 Saito Tsutomu
License: Python Software Foundation License
"""
import paramiko, os, sys, time, yaml
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
    for s in _manager.get_all_sshkeys():
        if s.name == name:
            return s.id
    return None

def image_id(name, private=False):
    for i in _manager.get_images(private):
        if i.name == name:
            return i.id

def droplet_id(name):
    for d in _manager.get_all_droplets():
        if d.name == name:
            return d.id

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
    d = do.Droplet(token=_manager.token, **dc)
    if not no_create:
        d.create()
        d.get_action(d.action_ids[0]).wait()
        d.load()
    return d

def ssh_client(dr, user=None):
    if not user:
        user = 'core' if dr.image['distribution'] == 'CoreOS' else 'root'
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


