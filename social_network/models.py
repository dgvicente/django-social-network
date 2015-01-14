#coding: utf-8
from django.contrib.auth import get_user_model
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from notifications.models import Event, NotificationTemplateConfig
from social_graph import Graph
from .utils import integrated_by_edge, member_of_edge, generate_sha1

User = get_user_model()


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='user_outgoing_friend_requests', verbose_name=_(u'Solicitante'))
    to_user = models.ForeignKey(User, related_name='user_incoming_friend_requests', verbose_name=_(u'Receptor'))
    message = models.TextField(null=True, blank=True, verbose_name=_(u'Mensaje'))
    accepted = models.BooleanField(default=False, verbose_name=_(u'Aceptada'))

    class Meta:
        app_label = 'social_network'

    def __unicode__(self):
        return self.to_user.get_full_name() or self.to_user.get_username()


class SocialGroup(models.Model):
    creator = models.ForeignKey(User, related_name='groups_created_by', verbose_name=_(u'Creador'))
    name = models.CharField(max_length=255, verbose_name=_(u'Nombre'))
    description = models.TextField(verbose_name=_(u'Descripción'))
    closed = models.BooleanField(default=False, verbose_name=_(u'Cerrado'))
    administrators = models.ManyToManyField(User, related_name='groups_administrated_by',
                                            verbose_name=_(u'Administradores'), null=True, blank=True)

    def images_upload(self, filename):
        salt, hash = generate_sha1(self.id)
        return 'site-%s/groups/%s/%s/%s/%s' % (
            settings.SITE_ID, '%s_%s' % (self._meta.app_label, self._meta.object_name.lower()), self.creator.pk, hash,
            filename)

    image = models.ImageField(verbose_name=_(u'Imagen'), upload_to=images_upload, null=True, blank=True, max_length=500)

    class Meta:
        app_label = 'social_network'

    @property
    def members_count(self):
        graph = Graph()
        edge = integrated_by_edge()
        return graph.edge_count(self, edge)

    @property
    def members(self):
        graph = Graph()
        edge = integrated_by_edge()
        count = graph.edge_count(self, edge)
        members = [user for user, attributes, time in graph.edge_range(self, edge, 0, count)]
        return list(set(members))

    def is_admin(self, user):
        return user.pk == self.creator.pk or user in self.administrators.all()

    def is_member(self, user):
        graph = Graph()
        edge = integrated_by_edge()
        return self.is_admin(user) or graph.edge_get(user, edge, self) is not None

    @staticmethod
    def user_group_count(user):
        graph = Graph()
        edge = member_of_edge()
        member_of_count = graph.edge_count(user, edge)
        creator_of = SocialGroup.objects.filter(creator=user).count()
        admin_of = 0  # SocialGroup.objects.filter(administrators__in=[user]).count()
        return member_of_count + creator_of + admin_of

    def __unicode__(self):
        return self.name


class GroupMembershipRequest(models.Model):
    requester = models.ForeignKey(User, related_name='requested_group_memberships', verbose_name=_(u'Solicitante'))
    group = models.ForeignKey(SocialGroup, related_name='aspirants', verbose_name=_(u'Grupo'))
    message = models.TextField(null=True, blank=True, verbose_name=_(u'Mensaje'))
    accepted = models.BooleanField(default=False, verbose_name=_(u'Aceptada'))

    class Meta:
        app_label = 'social_network'


class GroupPost(models.Model):
    creator = models.ForeignKey(User, related_name='(app_label)s_%(class)s_set_post')
    group = models.ForeignKey(SocialGroup, related_name='(app_label)s_%(class)s_set_post')
    comment = models.TextField()

    class Meta:
        abstract = True


class GroupComment(GroupPost):

    class Meta:
        app_label = 'social_network'


class GroupImage(GroupPost):
    def images_upload(self, filename):
        salt, hash = generate_sha1(self.id)
        return 'site-%s/groups_images/%s/%s/%s/%s' % (
            settings.SITE_ID, '%s_%s' % (self._meta.app_label, self._meta.object_name.lower()), self.creator.pk, hash,
            filename)

    image = models.ImageField(verbose_name=_(u'Imagen'), upload_to=images_upload, null=True, blank=True, max_length=500)

    class Meta:
        app_label = 'social_network'


class GroupFeedItem(models.Model):
    group = models.ForeignKey(SocialGroup)
    event = models.ForeignKey(Event)
    template_config = models.ForeignKey(NotificationTemplateConfig)

    site = models.ForeignKey(Site)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        app_label = 'social_network'

    def __init__(self, *args, **kwargs):
        super(GroupFeedItem, self).__init__(*args, **kwargs)
        if not self.pk and not self.site_id:
            self.site_id = self.event.site_id or Site.objects.get_current().pk


class FeedComment(models.Model):
    creator = models.ForeignKey(User, related_name='feed_comments')
    receiver = models.ForeignKey(User, related_name='feed_received_comments')
    comment = models.TextField()

    class Meta:
        app_label = 'social_network'

