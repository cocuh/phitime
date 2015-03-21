module.exports = function (grunt) {
  // Force use of Unix newlines
  grunt.util.linefeed = '\n';

  RegExp.quote = function (string) {
    return string.replace(/[-\\^$*+?.()|[\]{}]/g, '\\$&');
  };

  var fs = require('fs');
  var path = require('path');
  grunt.initConfig({
    pkg: grunt.file.readJSON('original/package.json'),
    banner: '/*!\n' +
      ' * Bootstrap v<%= pkg.version %> (<%= pkg.homepage %>)\n' +
      ' * Copyright 2011-<%= grunt.template.today("yyyy") %> <%= pkg.author %>\n' +
      ' * Licensed under <%= pkg.license.type %> (<%= pkg.license.url %>)\n' +
      ' */\n',
    clean: {
      dist: 'dist'
    },
    concat: {
      options: {
        banner: '<%= banner %>\n<%= jqueryCheck %>\n<%= jqueryVersionCheck %>',
        stripBanners: false
      },
      bootstrap: {
        src: [
          'original/js/transition.js',
          'original/js/alert.js',
          'original/js/button.js',
          'original/js/carousel.js',
          'original/js/collapse.js',
          'original/js/dropdown.js',
          'original/js/modal.js',
          'original/js/tooltip.js',
          'original/js/popover.js',
          'original/js/scrollspy.js',
          'original/js/tab.js',
          'original/js/affix.js'
        ],
        dest: 'dist/js/<%= pkg.name %>.js'
      }
    },

    uglify: {
      options: {
        preserveComments: 'some'
      },
      core: {
        src: '<%= concat.bootstrap.dest %>',
        dest: 'dist/js/<%= pkg.name %>.min.js'
      }
    },

    less: {
      compileCore: {
        options: {
          strictMath: true,
          sourceMap: true,
          outputSourceFiles: true,
          sourceMapURL: '<%= pkg.name %>.css.map',
          sourceMapFilename: 'dist/css/<%= pkg.name %>.css.map'
        },
        src: 'src/bootstrap.less',
        dest: 'dist/css/<%= pkg.name %>.css'
      },
      compileTheme: {
        options: {
          strictMath: true,
          sourceMap: true,
          outputSourceFiles: true,
          sourceMapURL: '<%= pkg.name %>-theme.css.map',
          sourceMapFilename: 'dist/css/<%= pkg.name %>-theme.css.map'
        },
        src: 'original/less/theme.less',
        dest: 'dist/css/<%= pkg.name %>-theme.css'
      }
    },

    cssmin: {
      options: {
        compatibility: 'ie8',
        keepSpecialComments: '*',
        noAdvanced: true
      },
      minifyCore: {
        src: 'dist/css/<%= pkg.name %>.css',
        dest: 'dist/css/<%= pkg.name %>.min.css'
      },
      minifyTheme: {
        src: 'dist/css/<%= pkg.name %>-theme.css',
        dest: 'dist/css/<%= pkg.name %>-theme.min.css'
      }
    },

    usebanner: {
      options: {
        position: 'top',
        banner: '<%= banner %>'
      },
      files: {
        src: 'dist/css/*.css'
      }
    },

    copy: {
      fonts: {
        expand: true,
        cwd: 'original/fonts/',
        src: '*',
        dest: 'dist/fonts/'
      }
    },
    
    watch:{
      src:{
        files:'<%= concat.bootstrap.src %>',
        tasks: ['concat', 'uglify']
      },
      less:{
        files:['original/less/*.less', '*.less'],
        tasks:['less', 'cssmin']
      }
    }
  });
  require('load-grunt-tasks')(grunt, { scope: 'devDependencies' });

  grunt.registerTask('default', ['clean:dist', 'concat', 'less', 'uglify', 'cssmin', 'copy:fonts'])
};