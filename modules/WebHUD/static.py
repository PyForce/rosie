from WebHUD import st


@st.task('coffee')
def coffee_task():
    src(r'static/coffee/.*\.coffee$')\
        .pipe(coffee(bare=True, executable=
                     'modules/WebHUD/node_modules/coffee-script/bin/coffee'))\
        .pipe(dest(output='modules/WebHUD/static/js/'))


@st.task('cjsx')
def cjsx_task():
    src(r'static/coffee/.*\.cjsx$')\
        .pipe(cjsx(bare=True, executable=
                   'modules/WebHUD/node_modules/coffee-react/bin/cjsx'))\
        .pipe(dest(output='modules/WebHUD/static/js/'))


@st.task('less')
def less_task():
    src(r'static/less/.*\.less$')\
        .pipe(less(executable='modules/WebHUD/node_modules/less/bin/lessc'))\
        .pipe(dest(output='modules/WebHUD/static/css/'))

st.runall()
