# The test cases should reside in tests*.py in order to be discoverable by
# unittest, and also should reside at the top level of the tests module to work
# with all Django versions. Other test utils are moved to a separated module to
# avoid loading of the test cases before Django initialisation, because this
# caused import errors with old Django version.
import os
import pickle

from django.core import mail
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase
from django.utils import translation

from . import send_mail, EmailMessage


CONTEXT2 = {'name': 'User2'}
SUBJECT2 = 'Hello User2'
BODY2 = 'User2, this is a plain text message.'


class BaseMailTestCase(TestCase):

    def _assertMessage(self, from_email, to, subject, body):
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.to, to)
        self.assertEqual(message.subject, subject)
        self.assertEqual(message.body, body)
        return message


class SendMailTestCase(BaseMailTestCase):

    def _send_mail(self, template_name, context, from_email, to,
                   res_subject, res_body, *args, **kwargs):
        send_mail(template_name, context, from_email, to, *args, **kwargs)
        return self._assertMessage(from_email, to, res_subject, res_body)

    def test_plain(self):
        self._send_mail(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_html(self):
        self._send_mail(
            'mail_templated_test/plain.html', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is an html message.')

    def test_multipart(self):
        message = self._send_mail(
            'mail_templated_test/multipart.html', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text part.')
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][0],
                         'User, this is an html part.')
        self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_multilang(self):
        translation.activate('en')
        self._send_mail(
            'mail_templated_test/multilang.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')
        translation.deactivate()

    def test_alternatives(self):
        message = self._send_mail(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.',
            alternatives=[('HTML alternative', 'text/html')])
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][0],
                         'HTML alternative')
        self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_multipart_alternatives(self):
        message = self._send_mail(
            'mail_templated_test/multipart.html', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text part.',
            alternatives=[('HTML alternative', 'text/html')])
        self.assertEqual(len(message.alternatives), 2)
        self.assertEqual(message.alternatives[0][0],
                         'HTML alternative')
        self.assertEqual(message.alternatives[0][1], 'text/html')
        self.assertEqual(message.alternatives[1][0],
                         'User, this is an html part.')
        self.assertEqual(message.alternatives[1][1], 'text/html')

    def test_attachment(self):
        file_name = os.path.join(os.path.dirname(__file__), 'test_utils',
                                 'attachment.png')
        with open(file_name, 'rb') as f:
            content = f.read()
        attachment = ('attachment.png', content, 'image/png')
        message = self._send_mail(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.',
            attachments=[attachment])
        self.assertEqual(len(message.attachments), 1)
        self.assertEqual(message.attachments[0], attachment)

    def test_extended(self):
        self._send_mail(
            'mail_templated_test/extended.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a base message.')

    def test_overridden(self):
        self._send_mail(
            'mail_templated_test/overridden.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Overridden hello User',
            'User, this is overridden message.')

    def test_overridden2(self):
        self._send_mail(
            'mail_templated_test/overridden2.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Overridden hello User',
            'User, this is overridden message.\nReally.')

    def test_whitespaces(self):
        self._send_mail(
            'mail_templated_test/whitespaces.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            '  User, this is a message with preceding and trailing whitespaces.  ')


class EmailMessageTestCase(BaseMailTestCase):

    def _send_mail(self, template_name, context, from_email, to,
                   res_subject, res_body, *args, **kwargs):
        message = EmailMessage(template_name, context, from_email, to,
                               *args, **kwargs)
        message.send()
        return self._assertMessage(from_email, to, res_subject, res_body)

    def test_plain(self):
        self._send_mail(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_defaults(self):
        self._send_mail(
            'mail_templated_test/empty.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Static subject',
            'Static body',
            subject='Static subject', body='Static body')

    def test_overridden_defaults(self):
        self._send_mail(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.',
            subject='Static subject', body='Static body')

    def test_late_init(self):
        message = EmailMessage()
        message.template_name = 'mail_templated_test/plain.tpl'
        message.context = {'name': 'User'}
        message.from_email = 'from@inter.net'
        message.to = ['to@inter.net']
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_load_template(self):
        message = EmailMessage(None, {'name': 'User'}, 'from@inter.net',
                               ['to@inter.net'])
        message.load_template('mail_templated_test/plain.tpl')
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_manual_load_template(self):
        message = EmailMessage(None, {'name': 'User'}, 'from@inter.net',
                               ['to@inter.net'])
        message.template = get_template('mail_templated_test/plain.tpl')
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_attach_alternative(self):
        message = EmailMessage(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'])
        message.attach_alternative('HTML alternative', 'text/html')
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')
        self.assertEqual(len(message.alternatives), 1)
        self.assertEqual(message.alternatives[0][0],
                         'HTML alternative')
        self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_pickling(self):
        message = EmailMessage(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'])
        self.assertEqual(message.template, None)
        dumped_message = pickle.dumps(message)
        message = pickle.loads(dumped_message)
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_pickling_rendered(self):
        message = EmailMessage(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'], render=True)
        self.assertNotEqual(message.template, None)
        dumped_message = pickle.dumps(message)
        message = pickle.loads(dumped_message)
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')

    def test_attach(self):
        message = EmailMessage(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            'from@inter.net', ['to@inter.net'])
        # Attach binary file because of strange encoding issue with textual
        # attachments on Django 1.6-1.8 and Python 3.
        file_name = os.path.join(os.path.dirname(__file__), 'test_utils',
                                 'attachment.png')
        message.attach_file(file_name, 'image/png')
        message.send()
        self._assertMessage(
            'from@inter.net', ['to@inter.net'], 'Hello User',
            'User, this is a plain text message.')
        self.assertEqual(len(message.attachments), 1)
        self.assertEqual(message.attachments[0][0], 'attachment.png')
        self.assertTrue(len(message.attachments[0][1]) > 0)
        self.assertEqual(message.attachments[0][2], 'image/png')


class RenderTestCase(BaseMailTestCase):

    def _initMessage(self, *args, **kwargs):
        return EmailMessage(
            'mail_templated_test/plain.tpl', {'name': 'User'},
            *args, **kwargs)

    def _assertIsRendered(self, message, is_rendered, subject='Hello User',
                          body='User, this is a plain text message.'):
        if is_rendered:
            self.assertEqual(message.subject, subject)
            self.assertEqual(message.body, body)
            self.assertTrue(message.is_rendered)
        else:
            self.assertEqual(message.subject, None)
            self.assertEqual(message.body, None)
            self.assertFalse(message.is_rendered)

    def test_init_render(self):
        message = self._initMessage(render=True)
        self._assertIsRendered(message, True)
        message.send()
        self._assertIsRendered(message, True)

    def test_init_norender(self):
        message = self._initMessage()
        self._assertIsRendered(message, False)
        message.send()
        self._assertIsRendered(message, True)

    def test_init_notrender(self):
        message = self._initMessage(render=False)
        self._assertIsRendered(message, False)

    def test_init_cantrender(self):
        self.assertRaises(TemplateDoesNotExist, EmailMessage, render=True)

    def test_manual_render(self):
        message = self._initMessage()
        message.render()
        self._assertIsRendered(message, True)
        message.context = CONTEXT2
        message.render()
        self._assertIsRendered(message, True, SUBJECT2, BODY2)
        message.send()
        self._assertIsRendered(message, True, SUBJECT2, BODY2)

    def test_manual_rerender(self):
        message = self._initMessage(render=True)
        message.context = CONTEXT2
        message.render()
        self._assertIsRendered(message, True, SUBJECT2, BODY2)
        message.send()
        self._assertIsRendered(message, True, SUBJECT2, BODY2)

    def test_manual_cantrender(self):
        message = EmailMessage()
        self.assertRaises(TemplateDoesNotExist, message.render)

    def test_send_notrendered(self):
        message = self._initMessage()
        message.context = CONTEXT2
        message.send()
        self._assertIsRendered(message, True, SUBJECT2, BODY2)

    def test_send_rendered(self):
        message = self._initMessage(render=True)
        message.context = CONTEXT2
        message.send()
        self._assertIsRendered(message, True)
