"""Generate Keys

Regenerates and distributes SSH keys.

Usage:
    sshdeploy [options] generate
    sshdeploy [options] test
    sshdeploy [options] distribute
    sshdeploy [options] clean
    sshdeploy manual

Options:
    -c <file>, --config-file <file>   file that contains list of keys to 
                                      generate and the hosts that should 
                                      receive the keys (sshdeploy.conf is 
                                      default).
    -d <name>, --keydir <name>        name of directory for holding new keys
                                      ('keys-YYYY-MM-DD' is default).
    -u <hosts>, --update <hosts>      hosts to update
    -s <hosts>, --skip <hosts>        hosts to skip
    -k <keys>, --keys <keys>          keys to update (only use with --trial-run)
    -t, --trial-run                   trial run (do not override ssh files)
    -n, --narrate                     narrate the process
    -v, --verbose                     narrate the process more verbosely
    -h, --help                        print usage summary

Keys and servers are specified with a comma separated list (no spaces).
""" 

# Imports {{{1
from .prefs import (
    DefaultKeygenOpts, DefaultAbraxasAccount, DefaultRemoteIncludeFilename
)
from .utils import date, test_access, clean
from .key import Key
from .authkeys import AuthKeys
from docopt import docopt
from shlib import to_path, Run, mkdir, cd, rm
from inform import (
    Inform, comment, display, done, error, fatal, os_error, terminate
)

def main():
    try:
        # Read command line {{{1
        cmdline = docopt(__doc__)
        keys = cmdline['--keys'].split(',') if cmdline['--keys'] else []
        update = cmdline['--update'].split(',') if cmdline['--update'] else []
        skip = cmdline['--skip'].split(',') if cmdline['--skip'] else []
        Inform(
            narrate=cmdline['--narrate'] or cmdline['--verbose'],
            verbose=cmdline['--verbose'],
            logfile='.sshdeploy.log',
            prog_name=False,
            flush=True
        )
        if keys and not cmdline['--trial-run']:
            fatal(
                'Using the --keys option results in incomplete authorized_keys files.',
                'It may only be used for testing purposes.',
                'As such, --trial-run must also be specified when using --keys.',
                sep='\n'
            )

        # Generated detailed help {{{1
        if cmdline['manual']:
            from pkg_resources import resource_string
            try:
                Run(
                    cmd=['less'], modes='soeW0',
                    stdin=resource_string('src', 'manual.rst').decode('utf8')
                )
            except OSError as err:
                error(os_error(err))
            terminate()

        # Read config file {{{1
        try:
            config_file = cmdline.get('--config-file')
            config_file = config_file if config_file else 'sshdeploy.conf'
            contents = to_path(config_file).read_text()
        except OSError as err:
            fatal(os_error(err))
        code = compile(contents, config_file, 'exec')
        config = {}
        try:
            exec(code, config)
        except Exception as err:
            fatal(err)

        # Move into keydir {{{1
        keydir = cmdline['--keydir']
        keydir = to_path(keydir if keydir else 'keys-' + date)
        if cmdline['generate']:
            comment('creating key directory:', keydir)
            rm(keydir)
            mkdir(keydir)
            cd(keydir)
        elif cmdline['distribute']:
            cd(keydir)

        # determine default values for key options
        defaults = {}
        for name, default in [
            ('keygen-options', DefaultKeygenOpts),
            ('abraxas-account', DefaultAbraxasAccount),
            ('remote-include-filename', DefaultRemoteIncludeFilename),
        ]:
            defaults[name] = config.get(name, default)

        # Generate keys {{{1
        if cmdline['generate']:
            for keyname in sorted(config['keys'].keys()):
                data = config['keys'][keyname]
                if keys and keyname not in keys:
                    # user did not request this key
                    continue

                # get default values for missing key options
                for option in defaults:
                    data[option] = data.get(option, defaults[option])

                # generate the key
                key = Key(keyname, data, update, skip, cmdline['--trial-run'])
                key.generate()

        # Publish keys {{{1
        elif cmdline['distribute']:
            for keyname in sorted(config['keys'].keys()):
                data = config['keys'][keyname]
                if keys and keyname not in keys:
                    continue # user did not request this key

                # get default values for missing key options
                for option in defaults:
                    data[option] = data.get(option, defaults[option])

                # publish the key pair to clients
                key = Key(keyname, data, update, skip, cmdline['--trial-run'])
                key.publish_private_key()
                key.gather_public_keys()

            # publish authorized_keys files to servers {{{1
            if cmdline['distribute']:
                for each in sorted(AuthKeys.known):
                    authkey = AuthKeys.known[each]
                    authkey.publish()
                    authkey.verify()

        # Process hosts {{{1
        elif cmdline['test'] or cmdline['clean']:
            hosts = set()
            for keyname, data in config['keys'].items():
                if keys and keyname not in keys:
                    continue # user did not request this key

                # add servers to list of hosts
                for server, options in data['servers'].items():
                    if update and server not in update or server in skip:
                        continue
                    if 'bypass' not in options:
                        hosts.add(server)

                # add clients to list of hosts
                for client in data['clients'].keys():
                    if update and client not in update or client in skip:
                        continue
                    hosts.add(client)

            # process the hosts
            if cmdline['test']:
                # test host
                for host in sorted(hosts):
                    test_access(host)
            else:
                # clean host
                for host in sorted(hosts):
                    clean(host)

    except OSError as err:
        error(os_error(err))
    except KeyboardInterrupt:
        display('Killed by user')
    done()
