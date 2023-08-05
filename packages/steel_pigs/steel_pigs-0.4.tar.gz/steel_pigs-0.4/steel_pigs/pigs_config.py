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

# this should be in the form of:
# from plugins.providers.sql import SQL
PROVIDER_PLUGIN = {
    "namespace": "steel_pigs.plugins.providers.sql",
    "class": "SQL",
    "engine": "sqlite:///:memory:",
}

VERSION_PROVIDER_PLUGIN = {
    "namespace": "steel_pigs.plugins.providers.static_version",
    "class": "StaticVersionProvider"
}

PXE_PROVIDER_PLUGIN = {
    "namespace": "steel_pigs.plugins.providers.static_pxe_provider",
    "class": "StaticPXEProvider"
}

FORMATTER_PROVIDER_PLUGIN = {
    "namespace": "steel_pigs.plugins.providers.noformat",
    "class": "NoFormatProvider"
}

ONLINE_COMPLETE_STATUS = "online"
PROVISION_STATUS = "provision"

PROVISION_PROVIDER_PLUGIN = {
    "namespace": "steel_pigs.plugins.providers.rpc_os_provision",
    "class": "RPCProvision"
}

# the app key for the flask app. This can be anything, and should be random and private
SECRET_KEY = "Some random string here for use with the flask_wtf forms."
