import MetadataRenderer
import mistune


def checkExist(txt):
    if txt is not None:
        return txt
    return 'post'


class Post:
    markdown = mistune.Markdown()

    def getRendered(self):
        return self.markdown(self.md)

    def __init__(self, filename):

        with open(filename, 'r') as f:
            output = f.read()
            f.close()

        data = MetadataRenderer.parse(output)

        self.title = data[0]['Title']
        self.date = data[0].get('Date')
        self.author = data[0].get('Author')
        self.template = checkExist(data[0].get('Template'))
        self.url = filename[6:-3] + '.html'
        self.md = data[1]
        self.rendered = self.markdown(self.md)
