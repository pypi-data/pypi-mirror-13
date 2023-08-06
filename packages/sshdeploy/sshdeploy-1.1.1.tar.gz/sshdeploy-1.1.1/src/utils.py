from shlib import Run, rm, to_path
from inform import comment, debug, display, error, fmt, narrate, os_error
from arrow import now

# today's date
date = now().format('YYYY-MM-DD')

# run a command
def run(cmd, stdin=None, modes=None):
    comment('    running:', *cmd)
    Run(cmd, stdin=stdin, modes=modes)

# run an sftp command
def run_sftp(server, cmds):
    cmd = ['sftp', '-q', '-b', '-', server]
    comment(fmt('    sftp {server}:'), '; '.join(cmds))
    try:
        Run(cmd, stdin='\n'.join(cmds), modes='sOEW')
    except KeyboardInterrupt:
        display('Continuing')

# test access to host
def test_access(host):
    try:
        narrate(fmt('Testing connection to {host}.'))
        payload = fmt('test payload for {host}')
        ref = to_path('.ref')
        test = to_path('.test')
        ref.write_text(payload)
        rm(test)
        run_sftp(host, [
            fmt('put {ref}'),
            fmt('get {ref} {test}'),
            fmt('rm {ref}')
        ])
        if test.read_text() == payload:
            comment(fmt('{host}: connection successful.'))
        else:
            error('cannot connect.', culprit=host)
    except OSError as err:
        error('cannot connect.', culprit=host)
    rm(ref, test)

# clean host
def clean(host):
    try:
        narrate(fmt('Cleaning {host}.'))
        run_sftp(host, ['rm .ssh/*.provisional'])
    except OSError as err:
        if 'no such file or directory' in str(err).lower():
            comment(os_error(err))
        else:
            error('cannot connect.', culprit=host)
