import subprocess
from flask_gulp import extension, File


@extension
def browserify(resources):
    executable = browserify.settings.get('executable') or 'browserify'
    bundle = browserify.settings.get('bundle') or 'bundle.js'

    command = "%s " % executable
    command += ' '.join((f.filename for f in resources))

    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()

    if process.returncode:
        yield File(filename=None, content=err, rel_name=None)
    else:
        yield File(filename=bundle, content=out, rel_name=None)
