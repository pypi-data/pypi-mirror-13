# -*- coding: utf-8 -*-
# Copyright 2016 Ionuț Arțăriși <ionut@artarisi.eu>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Return a function with any decorators removed """


__version__ = '0.1.1'


def undecorated(f):
    try:
        # python2
        closure = f.func_closure
    except AttributeError:
        pass

    try:
        # python3
        closure = f.__closure__
    except AttributeError:
        return

    if closure:
        for cell in closure:
            # avoid infinite recursion
            if cell.cell_contents is f:
                continue

            undecd = undecorated(cell.cell_contents)
            if undecd:
                return undecd
    else:
        return f
