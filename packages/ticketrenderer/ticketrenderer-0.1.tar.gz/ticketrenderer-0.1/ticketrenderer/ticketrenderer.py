# coding=utf-8

import random
from jinja2 import Environment


def datetimeformat(value, format='%Y-%m-%d'):
    """
    Jinja filter used to format date
    :param value:
    :param format:
    :return:
    """
    return value.strftime(format)

JINJA_ENV = Environment()
JINJA_ENV.filters['datetimeformat'] = datetimeformat


class TicketRenderer(object):

    def __init__(self, ticket_template, media_url, css_url):
        """
        :param ticket_template: a ticket template used to configure a photobooth
        :param media_url: base url to fetch images
        :param css_url: url to find css files
        :return:
        """
        self.template = ticket_template
        self.media_url = media_url
        self.css_url = css_url

    def render(self, picture, code, date):

        context = {
            'title': self.template['title'],
            'subtitle': self.template['subtitle'],
            'picture': picture,
            'datetime': date,
            'code': code
        }

        for image in self.template['images']:
            image_url = self.get_image_url(image['name'])
            context['image_%s' % image['id']] = image_url

        for image_variable in self.template['image_variables']:
            choice = random.choice(image_variable['items'])
            uid = 'imagevariable_%s' % image_variable['id']
            context[uid] = self.get_image_url(choice['name'])

        for text_variable in self.template['text_variables']:
            choice = random.choice(text_variable['items'])
            uid = 'textvariable_%s' % text_variable['id']
            context[uid] = choice

        template = JINJA_ENV.from_string(self.with_layout(self.template['html']))
        return template.render(context)

    def get_image_url(self, image_name):
        return '%s/images/%s' % (self.media_url, image_name)

    def with_layout(self, html):
        """
        add layout
        """
        base = u"""<!doctype html>
        <html class="figure figure-ticket-container">
            <head>
                <meta charset="utf-8">
                <link rel="stylesheet" href="{css_url}">
            </head>
            <body class="figure figure-ticket-container">
                <div class="figure figure-ticket">
                    {content}
                </div>
            </body>
        </html>"""
        return base.format(css_url=self.css_url, content=html)


