import argparse

# Attempt to import the JSON library.
try:
    import json
except ImportError:
    import simplejson

# Attempt to import the 'dopy' library.
try:
    from dopy.manager import DoManager
except:
    print('')

"""
An error that is thrown when the user has no droplets.
"""
class DataEmptyError(Exception):
    pass

"""
Digital Ocean Dynamic Inventory
---
A dynamic inventory script for Ansible that contains basic support for
grouping droplets.
"""
class DigitalOceanDynamicInventory(object):
    api_key = ""
    excluded_strings = []
    results = {}

    def __init__(self, api_key, excluded_strings = []):
        """
        Initialises the dynamic inventory generator and performs some basic
        checks.

        :param api_key: DigitalOcean API key
        :param excluded_strings: Strings to exclude from the grouping logic
        (i.e. .co.astal.io)
        :raises: ValueError
        """
        self.api_key = api_key
        self.excluded_strings = excluded_strings
        self.__validate_api_key()

    def run(self):
        """
        Runs the dynamic inventory generator.

        :rtype: str
        :return: The JSON or an error message.
        """
        try:
            droplets = self.get_droplets_from_digital_ocean()
            if not droplets:
                raise DataEmptyError()
            results = self.__perform_groupings(droplets)
            return json.dumps(results)
        except RuntimeError:
            return "failed=True msg='Connection error with DigitalOcean'"
        except DataEmptyError:
            return "failed=True msg='You have no droplets!'"

    def get_droplets_from_digital_ocean(self):
        """
        Yields the DigitalOcean droplets from the dopy library.

        :rtype: object[]
        :return: The DigitalOcean droplets in an array.
        """
        do = DoManager(None, self.api_key, api_version=2)
        return do.all_active_droplets()

    def __validate_api_key(self):
        """
        Ensures the API key is not null or empty.

        :raises: ValueError
        """
        if not self.api_key:
            raise ValueError("API_KEY is null or empty.")

    def __perform_groupings(self, droplets):
        """
        Performs the groupings on the droplets.

        :param droplets: The droplets array
        :rtype: object[]
        :return: The grouped DigitalOcean droplets
        """
        for droplet in droplets:
            working_name = self.__replace_excluded(droplet["name"])
            ip_address = droplet["ip_address"]
            self.__add_to_results("all", ip_address)

            # Ensure the . is in the working_name.
            if "." in working_name:
                # Loop through and forward split
                looping_name = working_name
                forward_contains_separator = True
                while forward_contains_separator:
                    looping_name, complete = self.__split_forward(looping_name,
                                                           ip_address)
                    forward_contains_separator = complete

                # Loop through and backwards split
                looping_name = working_name
                backward_contains_separator = True
                while backward_contains_separator:
                    looping_name, complete = self.__split_backward(
                        looping_name, ip_address)
                    backward_contains_separator = complete

        return self.results

    def __replace_excluded(self, droplet_name):
        """
        Remove the excluded strings from a droplet name.

        :param droplet_name: A droplet name to remove excluded strings from.
        :return: A working name with the excluded strings removed
        """
        working_name = droplet_name

        for string in self.excluded_strings:
            working_name = working_name.replace(string, "")

        return working_name

    def __split_forward(self, working_name, ip_address):
        """
        Performs the split of the . going forward

        :param working_name: The current working name
        :param ip_address: The IP address to add to the
        :return: A string ready to be split again.
        """
        split_working_name = working_name.split(".", 1)
        can_continue = len(split_working_name) > 1
        self.__add_to_results(split_working_name[0], ip_address)

        if can_continue:
            self.__add_to_results(split_working_name[1], ip_address)
            return split_working_name[1], can_continue

        return split_working_name[0], can_continue

    def __split_backward(self, working_name, ip_address):
        """
        Performs the split of the . going backwards.

        :param working_name: The current working name
        :param ip_address: The IP address to add to the
        :return: A string ready to be split again.
        """
        split_working_name = working_name.rsplit(".", 1)
        can_continue = len(split_working_name) > 1
        self.__add_to_results(split_working_name[0], ip_address)

        if can_continue:
            self.__add_to_results(split_working_name[1], ip_address)

        return split_working_name[0], can_continue

    def __add_to_results(self, group_name, ip_address):
        """
        Adds a group and an IP address to the results providing they
        don't exist already.

        :param group_name: The group name to add
        :param ip_address: The IP address to add
        """
        if group_name:
            group_name = self.__remove_trailing_separator(group_name)
            if group_name in self.results:
                if ip_address not in self.results[group_name]:
                    self.results[group_name].append(ip_address)
            else:
                self.results[group_name] = [ip_address]

    def __remove_trailing_separator(self, group_name):
        """
        Removes the trailing separator from a group name.

        :param group_name: The group name.
        :return: The group name with a trailing separator removed.
        """
        if group_name.endswith("."):
            return group_name[0:len(group_name) -1]

        return group_name

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory "
                                                 "for DigitalOcean that "
                                                 "supports the grouping of "
                                                 "droplets")

    # CLI argument requirements.
    parser.add_argument("apikey", help="DigitalOcean API key", type=str)
    parser.add_argument("-e", "--exclusions", help="Comma separated strings "
                                                   "to exclude from the "
                                                   "groups", type=str)
    parser.add_argument("--list", help="Lists all droplets and their "
                                       "groups", action="store_true")
    parser.add_argument("--host", help="Returns a singular host", type=str)

    args = parser.parse_args()

    # Set default exclusions (blank).
    if not args.exclusions:
        args.exclusions = ""

    # If Ansible is calling --host, return an emtpy dictionary.
    if args.host:
        print("{}")
    else:
        do = DigitalOceanDynamicInventory(args.apikey,
                                          args.exclusions.split(","))
        print(do.run())