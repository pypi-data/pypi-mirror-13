from django import template

from ..models import Recipient, Folder

import re

register = template.Library()


class Folders(template.Node):
    def __init__(self, user, var_name):
        self.user = template.Variable(user)
        self.var_name = var_name

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        folders = Folder.objects.filter(user=user)

        if self.var_name:
            context[self.var_name] = folders

        return ''


class MessageCount(template.Node):
    def __init__(self, from_user, var_name, to_user=None):
        self.user = template.Variable(from_user)
        self.var_name = var_name
        if to_user:
            self.to_user = template.Variable(to_user)
        else:
            self.to_user = to_user

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not self.to_user:
            message_count = Recipient.objects.count_unread_messages_for(user)

        else:
            try:
                to_user = self.to_user.resolve(context)
            except template.VariableDoesNotExist:
                return ''

            message_count = Recipient.objects.count_unread_messages_between(user,
                                                                            to_user)

        context[self.var_name] = message_count

        return ''


@register.tag
def get_folders_for(parser, token):
    """
    Returns the folders for a user

    Syntax::

        {% get_folders_for [user] as [var_name] %}

    Example usage::

        {% get_folders_for pero as folders %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)

    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    user, var_name = m.groups()
    return Folders(user, var_name)


@register.tag
def get_unread_message_count_for(parser, token):
    """
    Returns the unread message count for a user.

    Syntax::

        {% get_unread_message_count_for [user] as [var_name] %}

    Example usage::

        {% get_unread_message_count_for pero as message_count %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    user, var_name = m.groups()
    return MessageCount(user, var_name)


@register.tag
def get_unread_message_count_between(parser, token):
    """
    Returns the unread message count between two users.

    Syntax::

        {% get_unread_message_count_between [user] and [user] as [var_name] %}

    Example usage::

        {% get_unread_message_count_between funky and wunki as message_count %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) and (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    from_user, to_user, var_name = m.groups()
    return MessageCount(from_user, var_name, to_user)
