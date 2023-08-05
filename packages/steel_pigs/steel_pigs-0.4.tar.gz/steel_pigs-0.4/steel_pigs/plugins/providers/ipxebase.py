#   Copyright 2015 Michael Rice <michael@michaelrice.org>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import abc


class PXEProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_ipxe_script(self, *args, **kwargs):
        """
        Generates an iPXE script using the provided args and kwargs

        :param args:
        :param kwargs:
        :return:
        """
        return
