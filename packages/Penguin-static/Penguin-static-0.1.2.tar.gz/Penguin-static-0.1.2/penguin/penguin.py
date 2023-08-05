import json
"""
TODO:
get all the posts
"""


class Penguin:

    def __init__(self):

        with open('penguin.json') as f:
            obj = json.load(f)

        self.title = obj['title']
        self.posts = []
        self.source = obj['source']
        self.dest = obj['dest']
        self.Port = obj['Port']
