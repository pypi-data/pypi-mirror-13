# Copyright 2016 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Tools for handling Python3 hell
"""

from six import PY2

if PY2:

    def Bytes2Str(line):
        """
        Convert to str if it's a byte type

        :param line: str or bytes
        :return: string
        :rtype: str

        Convert `line` to str by decode() if it's a byte type. It's a good idea to do the setdefaultencoding() hack.
        """
        return line

    def SetDefaultEncoding(encoding='utf-8'):
        """
        Do the setdefaultencoding hack

        :param encoding: encoding (default: 'utf-8')
        :type encoding: str
        """
        import sys
        reload(sys)
        sys.setdefaultencoding(encoding)

else:

    def Bytes2Str(line):
        """
        Convert to str if it's a byte type

        :param line: str or bytes
        :return: string
        :rtype: str

        Convert `line` to str by decode() if it's a byte type. It's a good idea to do the setdefaultencoding() hack.
        """
        return line.decode(errors='replace') if line.__class__ is bytes else line

    def SetDefaultEncoding(encoding='utf-8'):
        """
        Do the setdefaultencoding hack

        :param encoding: encoding (default: 'utf-8')
        :type encoding: str
        """
