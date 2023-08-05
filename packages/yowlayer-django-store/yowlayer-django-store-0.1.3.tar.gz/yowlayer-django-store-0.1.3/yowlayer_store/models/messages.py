# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from yowlayer_store.models.conversations import Conversation
from yowlayer_store.models.contacts import Contact
from yowsup.layers.protocol_messages.protocolentities.message import MessageProtocolEntity


class Message(models.Model):
    id_gen = models.CharField(null=False, unique=True, max_length=64)
    conversation = models.ForeignKey(Conversation)
    created = models.DateTimeField(_("Date created"), auto_now_add=True)
    t_sent = models.DateTimeField(_("Date sent"), auto_now=True)
    content = models.TextField(_("Content"), null=True)

    def __unicode__(self):
        return self.id_gen

    def get_state(self):
        return MessageState.get_state(self)

    @classmethod
    def get_by_state(cls, states, conversation=None):
        if conversation:
            query = cls.objects.filter(states__state__in=states, conversation=conversation)
        else:
            query = cls.objects.filter(states__state__in=states)

        return query

    def to_dict(self):
        return {
            "id": self.id_gen,
            "conversation": self.conversation.to_dict(),
            "created": self.created,
            "content": self.content,
            "t_sent": self.t_sent,
            # TODO:Add media field to Message
            # if self.media is None else MessageProtocolEntity.MESSAGE_TYPE_MEDIA,
            "type": MessageProtocolEntity.MESSAGE_TYPE_TEXT,
            # "media": self.media.toDict() if self.media is not None else None,
            "state": self.get_state()
        }


class MessageState(models.Model):
    message = models.ForeignKey(Message, related_name="states")
    contact = models.ForeignKey(Contact, null=True, related_name="messages_states")
    RECEIVED, RECEIVED_REMOTE, RECEIVED_READ, RECEIVED_READ_REMOTE, SENT_QUEUED, SENT, SENT_DELIVERED, SENT_READ = (
        "received", "received_remote", "received_read", "received_read_remote", "sent_queued", "sent",
        "sent_delivered", "sent_read")
    STATE_CHOICES = (
        (RECEIVED, _("Received")),
        (RECEIVED_REMOTE, _("Received remote")),
        (RECEIVED_READ, _("Received read")),
        (RECEIVED_READ, _("Received read remote")),
        (SENT_QUEUED, _("Send queued")),
        (SENT, _("Sent")),
        (SENT_DELIVERED, _("Sent delivered")),
        (SENT_READ, _("Sent Read"))
    )
    state = models.CharField(_("state"), choices=STATE_CHOICES, max_length=128)

    def __unicode__(self):
        return "Message id: " + str(self.message) + " state: " + str(self.state)

    @classmethod
    def get_state(cls, message):
        try:
            return MessageState.objects.get(message=message).state
        except ObjectDoesNotExist:
            return None

    @classmethod
    def update_received_state(cls, message, state):
        try:
            mstate = MessageState.objects.get(message=message)
        except ObjectDoesNotExist:
            mstate = MessageState(message=message)
        mstate.state = state
        mstate.save()

    @classmethod
    def set_received(cls, message):
        cls.update_received_state(message, cls.RECEIVED)

    @classmethod
    def set_received_read_remote(cls, message):
        cls.update_received_state(message, cls.RECEIVED_READ_REMOTE)

    @classmethod
    def set_received_read(cls, message):
        cls.update_received_state(message, cls.RECEIVED_READ)

    @classmethod
    def set_received_remote(cls, message):
        cls.update_received_state(message, cls.RECEIVED_REMOTE)

    @classmethod
    def set_sent(cls, message):
        messageState, _ = MessageState.objects.get_or_create(message=message, state=cls.SENT_QUEUED)
        messageState.state = cls.SENT
        messageState.save()

    @classmethod
    def set_sent_queued(cls, message):
        messageState, _ = MessageState.objects.get_or_create(message=message, state=cls.SENT_QUEUED)
        messageState.save()

    @classmethod
    def set_sent_delivered(cls, message, contact=None):
        if contact:
            messageState = MessageState.objects.get(message=message, contact=contact)
        else:
            messageState = MessageState.objects.get(message=message)
        messageState.state = cls.SENT_DELIVERED
        messageState.save()

    @classmethod
    def set_sent_read(cls, message, contact=None):
        if contact:
            messageState = MessageState.objects.get(message=message, contact=contact)
        else:
            messageState = MessageState.objects.get(message=message)
        messageState.state = cls.SENT_READ
        messageState.save()
