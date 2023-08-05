import sys


class Utils(object):
    """Utilities and methods used in Kaptl class"""

    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is one of "yes" or "no".
        :param default:
        :param question:
        """
        valid = {"yes": "yes", "y": "yes", "ye": "yes",
                 "no": "no", "n": "no"}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while 1:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return default
            elif choice in valid.keys():
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    @staticmethod
    def read_rules_from_file(path):
        try:
            with open(path, "rb") as rules_file:
                return rules_file.read().decode("utf-8-sig")
        except IOError:
            print "ERROR: Couldn't read from a file. Check if you have a file named rules.kaptl in " \
                  "your current directory or if a path to your own rules file is correct."
            sys.exit()
