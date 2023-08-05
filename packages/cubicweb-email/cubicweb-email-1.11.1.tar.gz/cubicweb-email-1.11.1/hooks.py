"""hooks triggered on email entities creation:

* look for state change instruction (XXX security)
* set email content as a comment on an entity when comments are supported and
  linking information are found

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import re
import email

from logilab.common.umessage import UMessage
from logilab.mtconverter import TransformError

from cubicweb import UnknownEid
from cubicweb.mail import parse_message_id
from cubicweb.predicates import is_instance
from cubicweb.server import hook


def fix_ownership(cnx, eid, email):
    sender = email.senderaddr.email_of
    if sender and sender.e_schema == 'CWUser' and sender.eid != cnx.user.eid:
        # match a user which is not the connection's user, set owned_by / created_by
        cnx.execute('SET X owned_by U WHERE X eid %(x)s, U eid %(u)s',
                        {'x': eid, 'u': sender.eid})
        cnx.execute('SET X created_by U WHERE X eid %(x)s, U eid %(u)s',
                        {'x': eid, 'u': sender.eid})


class ExtractEmailInformation(hook.Operation):
    """generate a comment on the original entity if supported"""

    def precommit_event(self):
        email = self.email
        # should create a Comment ?
        info = self.info
        origeid = int(info['eid'])
        try:
            origetype = self.cnx.entity_metas(origeid)['type']
        except UnknownEid:
            self.error('email %s is referencing an unknown eid %s',
                       email.messageid, origeid)
            return
        if origetype in self.cnx.vreg.schema['comments'].objects('Comment'):
            try:
                part = email.parts_in_order(prefered_mime_type='text/plain')[0]
            except IndexError:
                pass
            else:
                try:
                    self.insert_comment(origeid, part)
                except:
                    self.exception('while generating comment on %s from email %s',
                                   origeid, email)

    def insert_comment(self, eid, emailpart):
        com = self.cnx.execute(
            'INSERT Comment C: C content %(content)s, '
            'C content_format %(format)s, C comments X, C generated_by E '
            'WHERE X eid %(x)s, E eid %(e)s',
            {'x': eid, 'e': self.email.eid, 'format': u'text/plain',
             'content': emailpart.actual_content()})
        fix_ownership(self.cnx, com[0][0], self.email)


class AnalyzeEmailText(hook.Operation):
    """check if there are some change state instruction in the mail content"""

    def precommit_event(self):
        text = self.email.subject or u''
        for part in self.email.parts_in_order(prefered_mime_type='text/plain'):
            try:
                text += ' ' + part.actual_content()
            except TransformError:
                continue
        # XXX use user session if gpg signature validated
        parser = self.cnx.vreg['components'].select('textanalyzer', self.cnx)
        parser.parse(self, text)

    def fire_event(self, event, evargs):
        if event == 'state-changed':
            evargs['trinfo'].cw_set(generated_by=self.email)
            fix_ownership(self.cnx, evargs['trinfo'].eid, self.email)


class AddEmailCommentHook(hook.Hook):
    """an email has been added, check if associated content should be created
    """
    __regid__ = 'extractmailcontent'
    __select__ = hook.Hook.__select__ & is_instance('Email')
    events = ('after_add_entity',)

    def __call__(self):
        if 'comments' in self._cw.repo.schema:
            for msgid in self.entity.references():
                info = parse_message_id(msgid, self._cw.vreg.config.appid)
                self.info('extracted information from message id %s: %s',
                          msgid, info)
                if info:
                    ExtractEmailInformation(self._cw, email=self.entity, info=info)
                    break
        AnalyzeEmailText(self._cw, email=self.entity)


CLEANUP_RGX = re.compile(r'\bre\s*:', re.I|re.U)
def cleanup_subject(string):
    return CLEANUP_RGX.sub('', string).strip()


class AddEmailPreHook(hook.Hook):
    __regid__ = 'extractmailmetadata'
    __select__ = hook.Hook.__select__ & is_instance('Email')
    events = ('before_add_entity',)

    def address_eid(self, address, alias=None):
        rql = 'Any X WHERE X is EmailAddress, X address LIKE %(addr)s'
        rset = self._cw.execute(rql, {'addr': address})
        if not rset:
            # create a new email address to link to
            alias = alias or None
            # XXX could try to link created address to a person
            eaddress = self._cw.create_entity('EmailAddress', address=address,
                                              alias=alias)
            return eaddress.eid
        # check for a prefered form if any
        return rset.get_entity(0, 0).prefered.eid

    def thread_eid(self, subject, replyeid):
        if replyeid:
            rset = self._cw.execute('EmailThread X WHERE Y in_thread X, Y eid %(y)s',
                                    {'y': replyeid})
            if rset:
                return rset[0][0]
        subject = cleanup_subject(subject)
        thread = self._cw.create_entity('EmailThread', title=subject)
        return thread.eid

    def __call__(self):
        msg = self.entity
        if 'headers' not in msg.cw_edited:
            return
        try:
            message = UMessage(email.message_from_string(msg.headers))
        except Exception:
            self.exception('bad message headers')
            return
        # XXX why limit to a single sender?
        if 'messageid' not in msg.cw_edited:
            msg.cw_edited['messageid'] = message.get('message-id')
        if 'subject' not in msg.cw_edited:
            msg.cw_edited['subject'] = message.get('subject') or u'(no subject)'
        if 'date' not in msg.cw_edited:
            msg.cw_edited['date'] = message.date()
        if 'sender' not in msg.cw_edited:
            sender = message.multi_addrs('from')[0]
            sendereid = self.address_eid(sender[1], sender[0])
            msg.cw_edited['sender'] = sendereid
        replyto = message.get('in-reply-to')
        if replyto and 'reply_to' not in msg.cw_edited:
            rset = self._cw.find('Email', messageid=replyto)
            if rset:
                # XXX reply_to should allow multiple objects
                msg.cw_edited['reply_to'] = rset[0][0]
        if 'in_thread' not in msg.cw_edited:
            msg.cw_edited['in_thread'] = self.thread_eid(msg.subject, msg.reply_to and msg.reply_to[0])


class AddEmailPostHook(AddEmailPreHook):
    events = ('after_add_entity',)

    def __call__(self):
        msg = self.entity
        if 'headers' not in msg.cw_edited:
            return
        try:
            message = UMessage(email.message_from_string(msg.headers))
        except Exception:
            return
        if not msg.cc:
            msg.cw_set(cc=[self.address_eid(addr, name)
                           for name, addr in message.multi_addrs('cc')])
        if not msg.recipients:
            msg.cw_set(recipients=set(self.address_eid(addr, name)
                                      for name, addr in message.multi_addrs('to')))
