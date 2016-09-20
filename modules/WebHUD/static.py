import subprocess

from WebHUD import st
from flask_gulp import extension


@st.task('coffee')
def coffee_task():
    src('static/coffee/**/*.coffee')\
        .pipe(coffee(bare=True, executable=
                     'node modules/WebHUD/node_modules/coffee-script/bin/'
                     'coffee'))\
        .pipe(dest(output='modules/WebHUD/static/bundle/'))


@st.task('cjsx')
def cjsx_task():
    src('static/coffee/**/*.cjsx')\
        .pipe(cjsx(bare=True, executable=
                   'node modules/WebHUD/node_modules/coffee-react/bin/cjsx'))\
        .pipe(dest(output='modules/WebHUD/static/bundle/'))


@st.task('less')
def less_task():
    src('static/less/**/*.less')\
        .pipe(less(executable='node modules/WebHUD/node_modules/less/bin/'
                   'lessc'))\
        .pipe(dest(output='modules/WebHUD/static/css/'))


@st.task('browserify')
def browserify():
    src('static/bundle/**/*.js')\
        .pipe(browserify())\
        .pipe(dest(output='modules/WebHUD/static/js/'))


@extension
def browserify(resources):
    executable = browserify.settings.get('executable') or 'browserify'
    bundle = browserify.settings.get('bundle') or 'bundle.js'

    command = "%s " % executable
    command += ' '.join((filename for filename, _ in resources))

    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()

    if process.returncode:
        yield None, err
    else:
        yield bundle, out
