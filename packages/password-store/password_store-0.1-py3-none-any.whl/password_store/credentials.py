from subprocess import run, PIPE

import yaml
from collections import Mapping

# TODO Support writing/changing the credentials file


class Credentials(Mapping):
    def __init__(self, name):
        self.__name = name
        self.__content = None
        self.__password = None
        self.__data = None

    def __getitem__(self, item):
        self.data[item]

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)

    @property
    def content(self) -> str:
        """
        The full content of the password entry
        """
        if self.__content is None:
            completed_process = run(['pass', self.__name], stdout=PIPE, universal_newlines=True)
            # TODO check return code to give back a meaningful error
            self.__content = completed_process.stdout  # type: str
            if '\n' in self.__content:
                self.__password, values_yaml = self.__content.split('\n', 1)
                self.__data = yaml.load(values_yaml)
            else:
                self.__password = self.__content
                self.__data = {}
        return self.__content

    @property
    def data(self) -> dict:
        """
        Data from the pass entry.

        From http://www.passwordstore.org/:

            The password store does not impose any particular schema or type of organization of your data, as it is
            simply a flat text file, which can contain arbitrary data. Though the most common case is storing a single
            password per entry, some power users find they would like to store more than just their password inside the
            password store, and additionally store answers to secret questions, website URLs, and other sensitive
            information or metadata. Since the password store does not impose a scheme of it's own, you can choose your
            own organization. There are many possibilities.

            One approach is to use the multi-line functionality of pass (--multiline or -m in insert), and store the
            password itself on the first line of the file, and the additional information on subsequent lines.

        This module makes use of this by assuming that everything after the first line is in yaml format.
        """
        if self.__data is None:
            if '\n' in self.content:
                _, data_yaml = self.content.split('\n', 1)
                self.__data = yaml.load(data_yaml)
            else:
                self.__data = {}
        return self.__data

    @property
    def password(self) -> str:
        """
        Fetches the password/first line from the pass entry.

        From http://www.passwordstore.org/:

            The --clip / -c options will only copy the first line of such a file to the clipboard, thereby making it
            easy to fetch the password for login forms, while retaining additional information in the same file.
        """
        if self.__password is None:
            self.__password = self.content.splitlines()[0]
        return self.__password