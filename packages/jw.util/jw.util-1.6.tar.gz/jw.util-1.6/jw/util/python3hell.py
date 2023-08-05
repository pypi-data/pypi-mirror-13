"""
Tools for handling Python3 hell
"""
from six import PY2

if PY2:

    def Bytes2Str(line):
        """
        Dummy: convert to str if it's a byte type

        :param line: str or bytes
        :return: string
        :rtype: str

        This is Python 2, so str is bytes and therefore, this function does nothing
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
        return line.decode() if line.__class__ is bytes else line

    def SetDefaultEncoding(encoding='utf-8'):
        """
        Do the setdefaultencoding hack

        :param encoding: encoding (default: 'utf-8')
        :type encoding: str
        """
