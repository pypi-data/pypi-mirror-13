# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import sys
import os
import subprocess
import tempfile

from ruamel.std.pathlib import Path
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from . import __version__

# docker-compose expects .yml
# docker-compose cannot handle author/description
# docker-compose cannot handle multiple documents

# prevent sexagesimals? http://stackoverflow.com/a/31007425/1307905


class DC2Service(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config
        self._config_dir = Path(self._config._file_name).parent

    def generate(self):
        for template in Path(__file__).with_name('template').glob('*'):
            target = self._config_dir / (template.stem + '.template')
            if not target.exists():
                target.write_bytes(template.read_bytes())
        file_name = None
        if self._args.dcyaml is None:
            cur_dir = Path('.')
            for ext in 'yml', 'yaml':
                tmp = cur_dir / ('docker-compose.' + ext)
                if tmp.exists():
                    file_name = tmp
                    break
            else:
                tmp = []
                for ext in 'yaml', 'yml':
                    tmp.extend(cur_dir.glob('*' + ext))
                if len(tmp) == 1:
                    file_name = tmp[0]
        else:
            file_name = Path(self._args.dcyaml)
        assert isinstance(file_name, Path)
        file_name = file_name.resolve()
        data = self._get_data(file_name)
        data['template'] = self._config_dir
        for path in os.environ['PATH'].split(':'):
            dc = Path(path) / 'docker-compose'
            if dc.exists() and dc.is_file():
                break
        else:
            print('docker-compose not found in PATH')
            sys.exit()
        data['dc'] = dc
        if self._args.respawn_limit:
            if self._args.respawn_limit[0] < 0:
                v = 'respawn limit unlimited'
            else:
                v = 'respawn limit {0} {1}\n'.format(*self._args.respawn_limit)
            data['respawnlimit'] = v  # empty string ok
        else:
            data['respawnlimit'] = ''  # empty string ok
        # print(ruamel.yaml.dump(data, allow_unicode=True))

        # data looks like:
        #
        # author: Anthon van der Neut <a.van.der.neut@ruamel.eu>
        # description: Mongo container
        # file: /opt/docker/mongo/docker-compose.yml
        # name: [mongo]   # a list of all container names, used to create service name
        # ports:          # per container name, any *public* ports
        #     mongo: [27017]
        if not self._args.upstart and not self._args.systemd:
            init_service = self.determine_init_service()
            if init_service == 'upstart':
                self._args.upstart = True
            elif init_service == 'systemd':
                self._args.systemd = True
            else:
                print('unknown service', init_service)
                sys.exit(1)
        # print(self._args.upstart, self._args.systemd)
        name = data['description']
        if data['ports']:
            p = set()
            for k in data['ports']:
                p.update(data['ports'][k])
            name += ' on port{} {}'.format('s' if len(p) > 1 else '',
                                           ', '.join([str(x) for x in sorted(p)]))
        data['description'] = name
        if not self._args.no_dc2service_author_info:
            data['author'] += ' (dc2service {})'.format(__version__)
        # for k in sorted(data):
        #     print(' ', k, '->', data[k])
        if self._args.upstart:
            self.gen_upstart(data)
        if self._args.systemd:
            self.gen_systemd(data)

    def gen_upstart(self, data):
        service_file = Path('/etc/init') / ('-'.join(data['name']) +
                                            '-docker.conf')
        template = (data['template'] / 'upstart.template').read_text()
        content = template.format(**data)
        print(content)
        tab_exp = Path('/etc/init.d/') / ('-'.join(data['name']) + '-docker')
        target = Path('/lib/init/upstart-job')
        if tab_exp.exists():
            assert tab_exp.resolve() == target
        # create the file
        td = Path(tempfile.mkdtemp(prefix='tmp_dc2service'))
        tf = td / service_file.name
        tf.write_text(content)
        print('>>>> writing', service_file)
        try:
            subprocess.call(['sudo', 'cp', str(tf), str(service_file)])
        except KeyboardInterrupt:
            sys.exit(1)
        td.rmtree()
        # create the link
        if not tab_exp.exists():
            print('>>>> creating', tab_exp)
            subprocess.call(['sudo', 'ln', '-s', str(target), str(tab_exp)])
        print('>>>> start with:')
        print('     sudo start {}'.format(service_file.stem))
        print('>>>> disable service with:')
        print('     echo manual | sudo tee /etc/init/{}.override'.format(service_file.stem))

    def gen_systemd(self, data):
        service_file = Path('/etc/systemd/system') / ('-'.join(data['name']) +
                                                      '-docker.service')

        template_file = data['template'] / 'systemd.template'
        template = template_file.read_text()
        up_d = u'up -d --no-recreate'
        if up_d in template and not self._args.up_d:
            for nr, line in enumerate(template.splitlines()):
                if up_d not in line:
                    continue
                if not line.startswith(u"ExecStart"):
                    continue
                print('Found "{}" in template {} (line: {})'.format(
                    up_d, template_file, nr))
                print('which is probably not ok. Remove the template file to have it updated,')
                print('edit it, or specify "--up-d" on the commandline')
            sys.exit(0)
        content = template.format(**data)
        print(content)
        td = Path(tempfile.mkdtemp(prefix='tmp_dc2service'))
        tf = td / service_file.name
        tf.write_text(content)
        print('>>>> writing', service_file)
        try:
            subprocess.call(['sudo', 'cp', str(tf), str(service_file)])
        except KeyboardInterrupt:
            sys.exit(1)
        td.rmtree()
        print('>>>> start with:')
        print('     sudo systemctl start {}'.format(service_file.stem))
        print('>>>> enable on reboot with:')
        print('     sudo systemctl enable {}'.format(service_file.stem))

    def _get_data(self, dc_file):
        _data = ruamel.yaml.load(dc_file.open(), Loader=ruamel.yaml.RoundTripLoader)
        assert isinstance(_data, CommentedMap)
        ret_val = {}
        error = False
        try:
            pre_comments = _data.ca.comment[1]
        except Exception as e:
            print(e)
            print('\nexception retrieving metadata comments from', dc_file)
            sys.exit(1)
        for pre_comment in pre_comments:
            if 'author:' in pre_comment.value:
                ret_val['author'] = pre_comment.value.split(':', 1)[1].strip()
            if 'description:' in pre_comment.value:
                ret_val['description'] = pre_comment.value.split(':', 1)[1].strip()
        container_names = []
        external_ports = {}
        for k in _data:
            service = _data[k]
            if 'container_name' not in service:
                print('service {} in {}, lacks a container_name'.format(k, dc_file))
                error = True
            else:
                name = service['container_name']
                container_names.append(name)
            for p in service.get('ports', []):
                if ':' in p:
                    external_ports.setdefault(name, []).append(int(p.split(':')[0]))
        # we need to have a description and a responsible person
        if 'author' not in ret_val:
            print('no author comment found in {}'.format(dc_file))
            error = True
        if 'description' not in ret_val:
            print('no author comment found in {}'.format(dc_file))
            error = True
        if error:
            sys.exit(1)
        ret_val['name'] = container_names
        ret_val['ports'] = external_ports
        ret_val['file'] = dc_file
        return ret_val

    def determine_init_service(self):
        """check OS for service type used """
        if 'systemd' in Path('/sbin/init').resolve().name:
            return 'systemd'
        try:
            res = subprocess.check_output(['/sbin/init', '--version']).decode('utf-8')
            if u'upstart' in res:
                return 'upstart'
        except subprocess.CalledProcessError as e:
            print('cannot determine init service\n', e.output, sep='')
            sys.exit(1)
        print('cannot determine init service\n', res, sep='')
        sys.exit(1)

    def templates(self):
        for name in self._config_dir.glob('*.template'):
            print(name.resolve())
