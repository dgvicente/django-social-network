# coding=utf-8
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from social_graph.api import Graph
        graph = Graph()
        graph.clear_cache()