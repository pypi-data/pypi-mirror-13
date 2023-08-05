import sys
import shutil
import os
import json
import glob
import threading
from .compiler import Compiler
from .penguin import Penguin
from .server import Server
from .post import Post
from .watcher import Watcher



def copyAndOverwrite(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


# Main method, this is the first thing to be executed and it takes the CLI
# commands
def main():
    args = []
    for arg in sys.argv:
        args.append(arg)
    execCommand(args)


# Execute the command given to the CLI
def execCommand(args):
    if args[1] == 'serve':
        serveSite()
    if args[1] == 'new':
        newSite(args[2])
    if args[1] == 'publish':
        publishPosts()


# Create a new site
def newSite(title):
    currentdir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(title):
        try:
            shutil.copytree(currentdir + '/generator', title)
            workingdir = os.getcwd()

            # Add site title to penguin.json
            with open(workingdir + '/' + title + '/penguin.json', 'r+') as f:
                data = json.load(f)
                data['title'] = title
                f.seek(0)
                json.dump(data, f, indent=4)
        except shutil.Error as e:
            print(e)
    # Raise error, directory already exists
    else:
        print("Directory already exists, please choose a different name")


# This method builds the site when it's served. It only compiles the Jinja files
# though. Markdown files (posts) are handled by the publishPosts method
def buildSite(site):
    if not os.path.isdir(site.dest):
        os.makedirs(site.dest)

    copyAndOverwrite('static', site.dest + '/static')

    files = []

    for file in glob.glob('*.html'):
        files.append(file)

    Compiler().compileJinja(site, files)


# Serve the site
def serveSite():
    site = Penguin()
    # Check if penguin.json is present, if not don't serve
    if os.path.isfile('penguin.json'):

        # Get all posts from the 'posts' directory
        for f in glob.glob('posts/*.md'):
            p = Post(f)
            site.posts.append(p)

        buildSite(site)

        # Watch directory for changes
        def watch():
            Watcher(site)

        t = threading.Thread(target=watch)
        t.start()
        Server(site)
    else:
        print("Please run this inside a penguin project directory")


# This method compiles the posts into .html
def publishPosts():
    site = Penguin()
    if os.path.isfile('penguin.json'):
        # The first statement is if the site hasn't been built yet
        # The second statement is if publish hasn't been run yet
        if not os.path.isdir(site.dest):
            os.makedirs(site.dest)
            os.makedirs(site.dest + '/posts')
        elif os.path.isdir(site.dest) and not os.path.isdir(site.dest+'/posts'):
            os.makedirs(site.dest + '/posts')

        posts = []

        for post in glob.glob('posts/*.md'):
            posts.append(post)

        Compiler().compileMarkdown(site, posts)
    else:
        print("Please run this inside a penguin project directory")


if __name__ == '__main__':
    main()
