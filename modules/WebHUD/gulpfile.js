var gulp = require('gulp');
var gutil = require('gulp-util');
var cjsx = require('gulp-cjsx');
var less = require('gulp-less');

var path = {
    coffee: ['./static/coffee/**/*.coffee',
             './static/coffee/**/*.cjsx'],
    less: ['./static/less/**/*.less']
}

gulp.task('coffee', function() {
  gulp.src(path.coffee)
    .pipe(cjsx({bare: true})
      .on('error', (data) => gutil.log(data.toString())))
    .pipe(gulp.dest('./static/js/'));
});

gulp.task('less', function() {
  gulp.src(path.less)
    .pipe(less({paths: path.less}))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('watch-coffee', function() {
  gulp.watch(path.coffee, ['coffee']);
});

gulp.task('watch-less', function() {
  gulp.watch(path.less, ['less']);
});

// The default task (called when you run `gulp` from cli)
gulp.task('default', ['watch-coffee', 'watch-less']);
