# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import os

from django.conf import settings

from multisync.models import LdapUser, LdapGroup
from multisync.nrpe import NrpeCheck


__author__ = 'Matthieu Gallet'


class ProsodySynchronizer(NrpeCheck):

    def synchronize(self):
        users = {x.name: x.display_name for x in LdapUser.objects.all()}
        parser = ConfigParser()
        for group in LdapGroup.objects.all():
            group = group.encode('utf-8')
            parser.add_section(group)
            for username in group.members:
                username = username.encode('utf-8')
                parser.set(group, '%s@%s' % (username, settings.PROSODY_DOMAIN), users.get(username, username))
        with open(settings.PROSODY_GROUP_FILE + '.tmp', 'w') as fd:
            parser.write(fd)
        os.rename(settings.PROSODY_GROUP_FILE + '.tmp', settings.PROSODY_GROUP_FILE)
