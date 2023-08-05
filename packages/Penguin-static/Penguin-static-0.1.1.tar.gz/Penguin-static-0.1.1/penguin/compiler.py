"""
This script compiles the templates for the static site.
All the compiled templates are stored in the 'site' directory.

"""

import os
import jinja2
from post import Post


# Check if the page directory exists
def checkExist(path):
    if os.path.exists(path):
        return True
    else:
        return False


# Get the filename where the output will be written
def getFilename(file, root, site):
    # If the file being compiled is index, no directory is needed
    if file == 'index.html' or file[2:] == 'index.html':
        if not root:
            return 'index.html'
        else:
            return site.dest + '/index.html'
    # Remove the '.html' extension
    dirname = file[:-5]
    filename = site.dest + '/' + dirname + '/index.html'
    # We are inside 'site/'
    if not root:
        filename = dirname+'/index.html'
        if not checkExist(dirname):
            os.mkdir(dirname)
    else:
        if not checkExist(site.dest + '/' + dirname):
            os.mkdir(site.dest + '/' + dirname)
    return filename


class Compiler:

    def compileJinja(self, site, files):
        # Since we are using the filesystem, we have to use Jinja's
        # FSL with the project directory as root
        # If we are recompiling, it means we are inside the site directory, so
        # the compiler cannot find the templates if the searchpath is working
        # dir, here we make sure to be in the project directory
        searchpath = site.source
        # We are inside the root dir of the folder
        root = True
        if os.getcwd()[-5:] == '/' + site.dest:
            searchpath = '..'
            root = False
        templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
        templateEnv = jinja2.Environment(loader=templateLoader)

        for file in files:
            print(file)
            template = templateEnv.get_template(file)
            output = template.render(site=site)
            filename = getFilename(file, root, site)

            with open(filename, 'w') as f:
                f.write(output)
                f.close()
        return

    def compileMarkdown(self, site, posts):
        # This is used to publish the posts
        # It takes the site instance and post titles as arguments

        # Go through each post title and create instance for each
        for f in posts:
            p = Post(f)

            searchpath = site.source
            templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
            templateEnv = jinja2.Environment(loader=templateLoader)

            templateName = p.template
            # render the template using the default post template
            # rendered is the final rendered document, pass the current post
            # instance to it and the site instance by default
            template = templateEnv.get_template('templates/'+templateName+'.html')
            rendered = template.render(post=p, site=site)

            filename = site.dest + '/' + f[:-3] + '.html'
            if os.getcwd()[-5:] == '/' + site.dest:
                filename = f

            with open(filename, 'w') as post:
                post.write(rendered)
                post.close()
