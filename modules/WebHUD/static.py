from WebHUD import st


@st.task('coffee')
def coffee_task():
    src('static/coffee/**/*.coffee')\
        .pipe(coffee(bare=True, executable=
                     'modules/WebHUD/node_modules/coffee-script/bin/coffee'))\
        .pipe(dest(output='modules/WebHUD/static/js/'))


@st.task('cjsx')
def cjsx_task():
    src('static/coffee/**/*.cjsx')\
        .pipe(cjsx(bare=True, executable=
                   'modules/WebHUD/node_modules/coffee-react/bin/cjsx'))\
        .pipe(dest(output='modules/WebHUD/static/js/'))


@st.task('less')
def less_task():
    src('static/less/**/*.less')\
        .pipe(less(executable='modules/WebHUD/node_modules/less/bin/lessc'))\
        .pipe(dest(output='modules/WebHUD/static/css/'))

