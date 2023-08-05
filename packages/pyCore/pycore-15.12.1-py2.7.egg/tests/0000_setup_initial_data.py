"""
Copyright (c) 2014 Maciej Nabozny

This file is part of CloudOver project.

CloudOver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from testutils import ssh_call
import settings
import urllib2


def setup_module(module):
    global core_address
    core_address = urllib2.urlparse.urlparse(settings.address).hostname


def teardown_module(module):
    pass


def setup_function(function):
    pass


def teardown_function(function):
    pass


def test_clean_storage():
    global core_address
    ssh_call(core_address, 'root', 'mount /storage')
    ssh_call(core_address, 'root', 'rm /storage/*')


def test_reset_db():
    global core_address
    ssh_call(core_address, 'root', 'rm /var/lib/cloudOver/overCluster.sqlite3')
    ssh_call(core_address, 'root', 'overCluster_admin syncdb --noinput')
    ssh_call(core_address, 'root', 'chown cloudover:cloudover /var/lib/cloudOver/overCluster.sqlite3')


def test_create_admin():
    global core_address
    script = '''from django.contrib.auth.models import User
user = User.objects.create_user('%s', 'someone@somehost.sometld', '%s')
user.is_staff = True
user.is_superuser = True
user.save()''' % (settings.admin_name, settings.admin_passwd)
    ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_add_small_template():
    global core_address
    script = '''from corecluster.models.core.template import Template
t = Template()
t.name = 'Small'
t.description = 'Small template description'
t.cpu = 1
t.memory = 128
t.points = 1
t.save()'''
    ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_add_medium_template():
    script = '''from corecluster.models.core.template import Template
t = Template()
t.name = 'Medium'
t.description = 'Medium template description'
t.cpu = 2
t.memory = 256
t.points = 2
t.save()'''
    ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_add_big_template():
    global core_address
    script = '''from corecluster.models.core.template import Template
t = Template()
t.name = 'Big'
t.description = 'Big template description'
t.cpu = 4
t.memory = 1024
t.points = 4
t.save()'''
    ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_add_network():
    global core_address
    script = '''from corecluster.models.core.available_network import AvailableNetwork
t = AvailableNetwork()
t.address = '10.250.0.0'
t.mode = 'routed'
t.access = 'public'
t.mask = 16
t.save()'''
    ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_add_storage():
    global core_address
    for storage in settings.storages:
        script = '''from corecluster.models.core.storage import Storage
t = Storage()
t.name = 'storage_%s'
t.address = '%s'
t.dir = '/storage'
t.state = 'locked'
t.capacity = 10000 # 10GB, for tests
t.save()''' % (storage, storage)
        ssh_call(core_address, 'root', 'echo "%s" | overCluster_admin shell' % script, 0)


def test_restart_apache():
    global core_address
    ssh_call(core_address, 'root', 'service apache2 restart', 0)


def test_restart_agents():
    global core_address
    ssh_call(core_address, 'root', 'service overcluster-core restart', 0)


def test_restart_quagga():
    global core_address
    ssh_call(core_address, 'root', 'service quagga restart', 0)

