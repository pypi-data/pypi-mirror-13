from django.core import mail
from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode


class EmailMessage(mail.EmailMultiAlternatives):
    """Extends standard EmailMessage class with ability to use templates"""

    def __init__(self, template_name=None, context={}, *args, **kwargs):
        """
        Initialize single templated email message (which can be sent to
        multiple recipients).

        When using with a user-specific message template for mass mailing,
        create new EmailMessage object for each user. Think about this class
        instance like about a single paper letter (you would not reuse it,
        right?).

        The class tries to provide interface as close to the standard Django
        classes as possible.
        The argument list is the same as in the base class except of two first
        parameters 'subject' and 'body' which are replaced with 'template_name'
        and 'context'. However you still can pass subject and body as keyword
        arguments to provide some static content if needed.

        Arguments:
            :param template_name: A name of template with optional blocks
                'subject', 'body' and 'html'.
            :type template_name: str
            :param context: A dictionary to be used for template rendering.
            :type context: bool

        Keyword Arguments:
            :param subject: Default message subject.
            :type subject: str
            :param body: Default message body.
            :type body: str
            :param render: If True, render template and evaluate 'subject' and
                'body' properties immediately.
            :type render: bool

        Other arguments are passed to the base class method as is.
        """
        self._subject = None
        self._body = None
        self._html = None
        self._rendered = False

        if (template_name):
            self.load_template(template_name)
        self.context = context

        subject = kwargs.pop('subject', None)
        body = kwargs.pop('body', None)
        render = kwargs.pop('render', False)

        super(EmailMessage, self).__init__(subject, body, *args, **kwargs)

        if render:
            self.render()

    @property
    def template(self):
        return self._template

    def load_template(self, template_name):
        """
        Load the template

        Arguments:
            :param template_name: A name of template with optional blocks
                'subject', 'body' and 'html'.
            :type template_name: str
        """
        # In Django 1.7 get_template() returned a django.template.Template.
        # In Django 1.8 it returns a django.template.backends.django.Template.
        template = get_template(template_name)
        self._template = getattr(template, 'template', template)

        # Prepare template blocks to not search them each time we send
        # a message.
        for block in self._template.nodelist:
            # We are interested in BlockNodes only. Ignore another elements.
            if isinstance(block, BlockNode):
                if block.name == 'subject':
                    self._subject = block
                elif block.name == 'body':
                    self._body = block
                if block.name == 'html':
                    self._html = block

    def render(self):
        """Render email with the current context"""
        # Prepare context
        context = Context(self.context)
        context.template = self.template
        # Assume the subject may be set manually.
        if self._subject is not None:
            self.subject = self._subject.render(context).strip('\n\r')
        # Same for body.
        if self._body is not None:
            self.body = self._body.render(context).strip('\n\r')
        # The html block is optional, and it also may be set manually.
        if self._html is not None:
            html = self._html.render(context).strip('\n\r')
            if html:
                if not self.body:
                    # This is html only message.
                    self.body = html
                    self.content_subtype = 'html'
                else:
                    # Add alternative content.
                    self.attach_alternative(html, 'text/html')
        self._rendered = True

    def send(self, *args, **kwargs):
        """
        Render email if needed and send it

        Arguments:
            :param render: If True, render template even if it is rendered
                already.
            :type render: bool

        Other arguments are passed to the base class method.
        """
        if kwargs.pop('render', False) or not self._rendered:
            self.render()
        return super(EmailMessage, self).send(*args, **kwargs)


    def __getstate__(self):
        """
        Exclude BlockNode and Template objects from pickling, b/c they can't
        be pickled.
        """
        return dict((k, v) for k, v in self.__dict__.iteritems()
                    if not k in ('_body', '_html', '_subject', '_template'))

    def __setstate__(self, state):
        """
        Use the template_name setter after unpickling so the orignal values of
        _body, _html, _subject and _template will be restored.
        """
        self.__dict__ = state
        self.template_name = self._template_name
