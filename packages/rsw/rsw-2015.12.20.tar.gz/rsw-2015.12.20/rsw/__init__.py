# core
import ConfigParser
import os

# 3rd party
import argh
from splinter import Browser

# local
import rswlib

def create_ini_file(i):
    config = ConfigParser.ConfigParser()
    config.add_section('login')

    print("Since this is your first time running rsw, we will configure your login info.")

    username = raw_input("Enter your username: ")
    password = raw_input("Enter your password: ")

    config.set('login', 'username', username)
    config.set('login', 'password', password)

    # Writing our configuration file to 'example.cfg'
    with open(i, 'wb') as configfile:
        config.write(configfile)

    return i


def config_file():
    home_dir = os.path.expanduser('~')
    ini_file = "{0}/rsw.ini".format(home_dir)
    if os.path.exists(ini_file):
        return ini_file
    else:
        return create_ini_file(ini_file)


def main(section='login', buy=True, autoclose=False):
    config = ConfigParser.ConfigParser()
    config.read(config_file())
    username = config.get(section, 'username')
    password = config.get(section, 'password')

    with Browser() as browser:

        browser.driver.set_page_load_timeout(30)

        e = rswlib.Entry(username, password, browser)

        e.login()

        if buy:
            e.exhaustive_buy()

        if not autoclose:
            loop_forever()


if __name__ == '__main__':
    argh.dispatch_command(main)