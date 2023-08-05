from bash.os import run


def autoincrement_tag(last_tag):
    """
    autoincrement_tag('1') => 2
    autoincrement_tag('1.2') => 1.3
    autoincrement_tag('1.2.3') => 1.2.4
    """
    tokens = last_tag.split('.')
    r = int(tokens[-1]) + 1
    if len(tokens) > 1:
        return '%s.%s' % ('.'.join(tokens[0:-1]), r)
    else:
        return str(r)

def current_git_branch():
    return run('git rev-parse --abbrev-ref HEAD')

def last_git_tag():
    return run('git describe --abbrev=0 --tags')

def create_tag(tag):
    return run('git tag %s && git push origin %s' % (tag, tag))

def auto_create_tag():
    tag = last_git_tag()
    if tag:
        tag = autoincrement_tag(tag)
    else:
        tag = '0.0.0'
    return create_tag(tag)

def reset_tag(tag):
    return run('git tag -d %s && git push origin :refs/tags/%s' % (tag, tag))

def reset_last_tag():
    tag = last_git_tag()
    return reset_tag(tag)
