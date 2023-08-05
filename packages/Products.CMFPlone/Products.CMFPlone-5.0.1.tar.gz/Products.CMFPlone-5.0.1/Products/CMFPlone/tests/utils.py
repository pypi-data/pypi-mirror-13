from persistent.list import PersistentList
import re

from Products.MailHost.MailHost import _mungeHeaders
from Products.MailHost.MailHost import MailBase
from Products.CMFPlone.patches.securemailhost import secureSend

# regexp for a valid CSS identifier without the leading #
VALID_CSS_ID = re.compile("[A-Za-z_@][A-Za-z0-9_@-]*")


def folder_position(context, position='', id=None, delta=1, reverse=None):
    """
    XXX Why is this here you ask?

    Well, we removed this from skins but we still test folder positions
    and ordering in CMFPlone so it was easier to use this.
    We do not use this any longer with new folder contents implementation
    """

    position = position.lower()
    if position == 'up':
        context.moveObjectsUp(id, delta=delta)
    elif position == 'down':
        context.moveObjectsDown(id, delta=delta)
    elif position == 'top':
        context.moveObjectsToTop(id)
    elif position == 'bottom':
        context.moveObjectsToBottom(id)
    # order folder by field
    # id in this case is the field
    elif position == 'ordered':
        context.orderObjects(id, reverse)
    context.plone_utils.reindexOnReorder(context)


class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.
    """

    def __init__(self, id):
        self.reset()

    def reset(self):
        self.messages = PersistentList()

    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """
        self.messages.append(messageText)

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self.messages.append(messageText)

    # Outside of the tests we patch the MailHost to provide a
    # secureSend method for backwards compatibility, so we should do
    # that for our MockMailHost as well.
    secureSend = secureSend


# a function to test if a string is a valid CSS identifier
def validateCSSIdentifier(identifier):
    match = VALID_CSS_ID.match(identifier)
    if not match is None:
        return match.end() == len(identifier)
    else:
        return False
