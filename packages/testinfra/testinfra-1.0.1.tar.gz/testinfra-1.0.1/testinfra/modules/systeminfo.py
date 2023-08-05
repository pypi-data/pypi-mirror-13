# -*- coding: utf8 -*-
# Copyright © 2015 Philippe Pepiot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from testinfra.modules.base import InstanceModule


class SystemInfo(InstanceModule):
    """Return system informations"""

    def __init__(self):
        self._sysinfo = None
        super(SystemInfo, self).__init__()

    @property
    def sysinfo(self):
        if self._sysinfo is None:
            self._sysinfo = self.get_system_info()
        return self._sysinfo

    def get_system_info(self):
        sysinfo = {
            "type": None,
            "distribution": None,
            "codename": None,
            "release": None,
        }
        sysinfo["type"] = self.check_output("uname -s").lower()
        if sysinfo["type"] == "linux":
            lsb = self.run("lsb_release -a")
            if lsb.rc == 0:
                for line in lsb.stdout.splitlines():
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip().lower()
                    if key == "distributor id":
                        sysinfo["distribution"] = value
                    elif key == "release":
                        sysinfo["release"] = value
                    elif key == "codename":
                        sysinfo["codename"] = value
            else:
                os_release = self.run("cat /etc/os-release")
                if os_release.rc == 0:
                    for line in os_release.stdout.splitlines():
                        for key, attname in (
                            ("ID=", "distribution"),
                            ("VERSION_ID=", "release"),
                        ):
                            if line.startswith(key):
                                sysinfo[attname] = (
                                    line[len(key):].replace('"', "").
                                    replace("'", "").strip())
        else:
            sysinfo["release"] = self.check_output("uname -r")
            sysinfo["distribution"] = sysinfo["type"]
            sysinfo["codename"] = None
        return sysinfo

    @property
    def type(self):
        """OS type

        >>> SystemInfo.type
        'linux'
        """
        return self.sysinfo["type"]

    @property
    def distribution(self):
        """Distribution name

        >>> SystemInfo.distribution
        'debian'
        """
        return self.sysinfo["distribution"]

    @property
    def release(self):
        """Distribution release number

        >>> SystemInfo.release
        '7.8'
        """
        return self.sysinfo["release"]

    @property
    def codename(self):
        """Release code name

        >>> SystemInfo.codename
        'wheezy'
        """
        return self.sysinfo["codename"]

    @property
    def user(self):
        return self.check_output("id -nu")

    @property
    def uid(self):
        return int(self.check_output("id -u"))

    @property
    def group(self):
        return self.check_output("id -ng")

    @property
    def gid(self):
        return int(self.check_output("id -g"))

    @property
    def hostname(self):
        return self.check_output("hostname -s")
