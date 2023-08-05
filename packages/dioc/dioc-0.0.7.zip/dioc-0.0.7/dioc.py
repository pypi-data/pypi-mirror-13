"""
Copyright: 2016 Saito Tsutomu
License: Python Software Foundation License
"""
import paramiko, os, re, sys, time
import digitalocean as do

class _Manager(do.Manager):
    def __init__(self):
        self.token = os.environ.get('DIOC_TOKEN')
        self.default_sshkey = os.environ.get('DIOC_DEFAULT_SSHKEY')
        self.default_size = os.environ.get('DIOC_DEFAULT_SIZE', '512mb')
        self.default_region = os.environ.get('DIOC_DEFAULT_REGION', 'sgp1')
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

def create_droplet(dr):
    try:
        dr.create()  
        dr.get_action(dr.action_ids[0]).wait()
        dr.load()
    except Exception as e:
        sys.stderr.write('%s\n' % e)

def Droplet(name, image=None, size=None, region=None,
            ssh_keys=None, no_create=False, **kwargs):
    if not image:
        image = _manager.get_image('coreos-stable').id
    else:
        image = image_id(image)
    dc = {'name': name, 'image': image}
    dc.update(kwargs)
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
        create_droplet(dr)
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

def ssh_client(dr, user=None, **kwargs):
    if not user:
        user = ssh_user(dr)
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ip = dr.ip_address
    for i in range(6):
        try:
            time.sleep(1)
            cli.connect(ip, username=user, **kwargs)
            return cli
        except:
            pass
    else:
        sys.stderr.write('paramiko.connect error\n')

_manager = _Manager()
