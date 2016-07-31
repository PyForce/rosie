from WebHUD import st
from flask_static.extensions import extension
from os.path import splitext
from subprocess import Popen, PIPE

@st.task('coffee')
def coffee_task():
    src(r'static/coffee/.*\.coffee$')\
        .pipe(coffee(bare=True))\
        .pipe(dest(output='modules/WebHUD/static/js/'))

@st.task('cjsx')
def cjsx_task():
    src(r'static/coffee/.*\.cjsx$')\
        .pipe(cjsx(bare=True))\
        .pipe(dest(output='modules/WebHUD/static/js/'))

@st.task('less')
def less_task():
    src(r'static/less/.*\.less$')\
            .pipe(less())\
            .pipe(dest(output='modules/WebHUD/static/css/'))

# overwrite coffee extension
@extension
def coffee(filename, data):
    bare = coffee.settings.get('bare')
    command = ['modules/WebHUD/node_modules/coffee-script/bin/coffee', '-c',
               '-s']
    if bare:
        command += ['-b']
    return runner(command, filename, data, '.js')

@extension
def cjsx(filename, data):
    bare = cjsx.settings.get('bare')
    command = ['modules/WebHUD/node_modules/coffee-react/bin/cjsx', '-c', '-s']
    if bare:
        command += ['-b']
    return runner(command, filename, data, '.js')

@extension
def less(filename, data):
    return runner(['modules/WebHUD/node_modules/less/bin/lessc', '-'],
                  filename, data, '.css')

def runner(command, filename, data, ext):
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate(data)

    if process.returncode:
        return None, err
    else:
        _, cext = splitext(filename)
        dest = filename.replace(cext, ext)
        return dest, out

st.runall()
