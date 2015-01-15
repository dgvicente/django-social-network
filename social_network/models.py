#coding: utf-8
from django.contrib.auth import get_user_model
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.db.models import permalink
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from notifications.models import Event, NotificationTemplateConfig
from social_graph import Graph
from .signals import (
    social_group_member_added,
    social_group_created,
    friend_request_created,
    social_group_membership_request_created,
    social_group_photo_created,
    social_group_comment_created,
    feed_comment_created
)
from .utils import integrated_by_edge, member_of_edge, generate_sha1, group_comment_event_type, group_photo_event_type

User = get_user_model()
graph = Graph()


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='user_outgoing_friend_requests', verbose_name=_(u'Requester'))
    to_user = models.ForeignKey(User, related_name='user_incoming_friend_requests', verbose_name=_(u'Receiver'))
    message = models.TextField(null=True, blank=True, verbose_name=_(u'Message'))
    accepted = models.BooleanField(default=False, verbose_name=_(u'Accepted'))
    denied = models.BooleanField(default=False, verbose_name=_(u'Denied'))

    class Meta:
        app_label = 'social_network'

    def __unicode__(self):
        return self.to_user.get_full_name() or self.to_user.get_username()

    def accept(self, by_user):
        if by_user != self.to_user or self.denied or self.accepted:
            return False
        if self.to_user.make_friend_of(self.from_user):
            self.accepted = True
            self.save()
            return True
        else:
            raise Exception("A problem has occurred while trying to create a friendship edge.")

    def deny(self, by_user):
        if by_user != self.to_user or self.accepted or self.denied:
            return False
        self.denied = True
        self.save()
        return True


@receiver(post_save, sender=FriendRequest, dispatch_uid='post_save_friend_request')
def post_save_friend_request(sender, instance, created, **kwargs):
    if created:
        friend_request_created.send(
            sender=FriendRequest,
            user=instance.from_user,
            instance=instance,
            receiver=instance.to_user
        )


class SocialGroupManagerMixin(object):

    def integrated_by(self, user):
        member_of = member_of_edge()
        count = graph.edge_count(user, member_of)
        ids = [node.pk for node, attributes, time in graph.edge_range(user, member_of, 0, count)]
        return self.get_queryset().filter(pk__in=ids)


class SocialGroupManager(SocialGroupManagerMixin, models.Manager):
    pass


class SocialGroupCurrentSiteManager(SocialGroupManagerMixin, CurrentSiteManager):
    pass


class SocialGroup(models.Model):
    creator = models.ForeignKey(User, related_name='groups_created_by', verbose_name=_(u'Creator'))
    name = models.CharField(max_length=255, verbose_name=_(u'Name'))
    description = models.TextField(verbose_name=_(u'Description'))
    closed = models.BooleanField(default=False, verbose_name=_(u'Closed'))
    administrators = models.ManyToManyField(User, related_name='groups_administrated_by',
                                            verbose_name=_(u'Administrators'), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    site = models.ForeignKey(Site)

    def images_upload(self, filename):
        salt, hash = generate_sha1(self.id)
        return 'site-%s/groups/%s/%s/%s/%s' % (
            self.site, '%s_%s' % (self._meta.app_label, self._meta.object_name.lower()), self.creator.pk, hash,
            filename)

    image = models.ImageField(verbose_name=_(u'Image'), upload_to=images_upload, null=True, blank=True, max_length=500)

    objects = SocialGroupManager()
    on_site = SocialGroupCurrentSiteManager()

    class Meta:
        app_label = 'social_network'

    def __init__(self, *args, **kwargs):
        super(SocialGroup, self).__init__(*args, **kwargs)
        if not self.pk and not self.site_id:
            self.site_id = Site.objects.get_current().pk

    @permalink
    def get_absolute_url(self):
        return "social_group_details", [self.pk]

    @property
    def members(self):
        return graph.edge_count(self, integrated_by_edge())

    @property
    def member_list(self):
        edge = integrated_by_edge()
        count = graph.edge_count(self, edge)
        return [user for user, attributes, time in graph.edge_range(self, edge, 0, count)]

    def specific_role_member_list(self, role):
        edge = integrated_by_edge()
        count = graph.edge_count(self, edge)
        return [user for user, attributes, time in graph.edge_range(self, edge, 0, count) if attributes['role'] == role]

    @property
    def member_role_list(self):
        edge = integrated_by_edge()
        count = graph.edge_count(self, edge)
        return dict([(user.pk, attributes.get('role', 'member'))
                     for user, attributes, time in graph.edge_range(self, edge, 0, count)])

    def has_admin(self, user):
        return user == self.creator or user in self.administrators.all()

    def has_member(self, user):
        return graph.edge_get(user, member_of_edge(), self) is not None

    def relationship_with(self, user):
        edge = graph.edge_get(user, member_of_edge(), self)
        return user, edge.attributes.get('role', 'member') if edge else None

    def add_member(self, member, acceptor=None):
        if not acceptor:
            acceptor = member
        if self.closed and not self.has_admin(acceptor):
            return False
        _edge = graph.edge(member, self, member_of_edge(), self.site, {'role': 'member'})
        if _edge:
            social_group_member_added.send(
                sender=SocialGroup,
                group=self,
                member=member,
                user=acceptor
            )
            return True
        else:
            raise Exception("A problem has occurred while trying to create a membership edge.")

    def __unicode__(self):
        return self.name


@receiver(post_save, sender=SocialGroup, dispatch_uid='post_save_social_group')
def post_save_social_group(sender, instance, created, **kwargs):
    if created:
        # add creator to members
        graph.edge(instance.creator, instance, member_of_edge(), instance.site, {'role': 'creator'})
        social_group_created.send(sender=SocialGroup, instance=instance, user=instance.creator)


@receiver(m2m_changed, sender=SocialGroup.administrators.through, dispatch_uid='post_m2m_changed_social_group')
def post_m2m_changed_social_group(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    member_of = member_of_edge()
    if not reverse:  # the call has modified the direct relationship SocialGroup.administrators
        group = instance
        if action == 'post_clear':
            for admin in group.specific_role_member_list('admin'):
                graph.no_edge(admin, group, member_of, group.site)
        else:
            admins = model.objects.filter(pk__in=list(pk_set))
            if action == 'post_add':
                for admin in admins:
                    graph.edge(admin, group, member_of, group.site, {'role': 'admin'})
            elif action == 'post_remove':
                for admin in admins:
                    graph.no_edge(admin, group, member_of, group.site)
    else:  # the call has modified the reverse relationship: User.groups_administrated_by
        admin = instance
        if action == 'post_clear':
            for group in admin.specific_role_social_group_list('admin'):
                graph.no_edge(admin, group, member_of, group.site)
        else:
            groups = model.objects.filter(pk__in=list(pk_set))
            if action == 'post_add':
                for group in groups:
                    graph.edge(admin, group, member_of, group.site, {'role': 'admin'})
            elif action == 'post_remove':
                for group in groups:
                    graph.no_edge(admin, group, member_of, group.site)


class GroupMembershipRequest(models.Model):
    requester = models.ForeignKey(User, related_name='requested_group_memberships', verbose_name=_(u'Requester'))
    group = models.ForeignKey(SocialGroup, related_name='aspirants', verbose_name=_(u'Group'))
    message = models.TextField(null=True, blank=True, verbose_name=_(u'Message'))
    accepted = models.BooleanField(default=False, verbose_name=_(u'Accepted'))
    denied = models.BooleanField(default=False, verbose_name=_(u'Denied'))
    acceptor = models.ForeignKey(
        User, related_name='accepted_group_memberships', verbose_name=_(u'Decider'), null=True, blank=True
    )

    class Meta:
        app_label = 'social_network'

    def accept(self, by_user):
        if not by_user.is_admin_of(self.group) or self.denied or self.accepted:
            return False
        if self.group.add_member(self.requester, by_user):
            self.accepted = True
            self.acceptor = by_user
            self.save()
            return True
        else:
            return False

    def deny(self, by_user):
        if not by_user.is_admin_of(self.group) or self.accepted or self.denied:
            return False
        self.denied = True
        self.acceptor = by_user
        self.save()
        return True


@receiver(post_save, sender=GroupMembershipRequest, dispatch_uid='post_save_group_membership_request')
def post_save_group_membership_request(sender, instance, created, **kwargs):
    if created:
        social_group_membership_request_created.send(
            sender=GroupMembershipRequest,
            instance=instance,
            user=instance.requester,
            group=instance.group
        )


class GroupPost(models.Model):
    creator = models.ForeignKey(User, related_name='(app_label)s_%(class)s_set_post')
    group = models.ForeignKey(SocialGroup, related_name='(app_label)s_%(class)s_set_post')
    comment = models.TextField()

    class Meta:
        abstract = True


class GroupComment(GroupPost):

    class Meta:
        app_label = 'social_network'


@receiver(post_save, sender=GroupComment, dispatch_uid='post_save_group_comment')
def post_save_group_comment(sender, instance, created, **kwargs):
    if created:
        social_group_comment_created.send(sender=GroupComment, user=instance.creator, instance=instance)


@receiver(social_group_comment_created, sender=GroupComment)
def social_network_group_comment(instance, user, **kwargs):
    from notifications import create_event
    create_event(user, group_comment_event_type(), instance, _(u'A comment has been posted in a group'))


class GroupImage(GroupPost):
    def images_upload(self, filename):
        salt, hash = generate_sha1(self.id)
        return 'site-%s/groups_images/%s/%s/%s/%s' % (
            settings.SITE_ID, '%s_%s' % (self._meta.app_label, self._meta.object_name.lower()), self.creator.pk, hash,
            filename)

    image = models.ImageField(verbose_name=_(u'Image'), upload_to=images_upload, null=True, blank=True, max_length=500)

    class Meta:
        app_label = 'social_network'


@receiver(post_save, sender=GroupImage, dispatch_uid='post_save_group_image')
def post_save_group_image(sender, instance, created, **kwargs):
    if created:
        social_group_photo_created.send(sender=GroupImage, user=instance.creator, instance=instance)


@receiver(social_group_photo_created, sender=GroupImage)
def social_network_group_photo(instance, user, **kwargs):
    from notifications import create_event
    create_event(user, group_photo_event_type(), instance, _(u'A photo has been posted in a group'))


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


@receiver(post_save, sender=FeedComment, dispatch_uid='post_save_feed_comment')
def post_save_feed_comment(sender, instance, created, **kwargs):
    if created:
        feed_comment_created.send(sender=FeedComment, user=instance.creator, instance=instance)