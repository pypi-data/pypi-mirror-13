from docutils import nodes
from docutils.parsers.rst import Directive
from fountain import Fountain

def append_dialogue(container, token):
    char = nodes.line()
    char += nodes.Text(token['character'])
    char.attributes['classes'] = [ 'dialog-character' ]
    container += char

    line = nodes.line()
    line += nodes.Text('\n'.join(token['text']))
    line.attributes['classes'] = [ 'dialog-text' ]
    container += line

def append_action(container, token):
    line = nodes.line()
    line += nodes.Text('\n'.join(token['lines']))
    line.attributes['classes'] = [ 'action' ]
    container += line

def append_transition(container, token):
    line = nodes.line()
    line += nodes.Text(token['transition'] + ':')
    container += line

def append_slugline(container, token):
    line = nodes.line()
    forced = token.get('forced')
    if forced:
        line += nodes.Text(token['description'])
    else:
        line += nodes.Text(token.get('place', '') + '. ')
        line += nodes.Text(token.get('location', ''))
        time = token.get('time', '')
        if time:
            line += nodes.Text(' -- ')
        line += nodes.Text(time)

    line.attributes['classes'] = [ 'slugline' ]
    container.append(line)

def nothing(container, token):
    print('do nothing with', token, token['type'])

token_builder_by_type = {
    'dialogue': append_dialogue,
    'action': append_action,
    'slugline': append_slugline,
    'transition': append_transition,
}

def setup(app):
    app.add_directive('fountain', FountainDirective)
    return { 'version': '0.1.4' }

class FountainDirective(Directive):
    has_content = True
    def run(self):
        parser = Fountain()
        tokens = parser.tokenize(self.content)
        container = nodes.container()
        for token in tokens:
            token_builder_by_type.get(token['type'], nothing)(container, token)
        container.attributes['classes'] = [ 'screenplay' ]
        return [ container ]
