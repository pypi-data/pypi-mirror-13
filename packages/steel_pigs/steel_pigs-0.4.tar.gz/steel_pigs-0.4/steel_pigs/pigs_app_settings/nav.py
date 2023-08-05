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

from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

# To keep things clean, we keep our Flask-Nav instance in here. We will define
# frontend-specific navbars in the respective frontend, but it is also possible
# to put share navigational items in here.

nav = Nav()

nav.register_element('frontend_top', Navbar(
    View('Search By Name', '.find_by_name'),
    Subgroup(
        'Docs',
        Link('PIGS WIKI', 'https://github.com/virtdevninja/steel_pigs/wiki'),
        Link('Making PIGS Plugins', 'https://github.com/virtdevninja/steel_pigs/wiki'),
    ),
))
