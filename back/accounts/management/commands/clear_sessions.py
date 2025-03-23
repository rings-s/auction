# Path: accounts/management/commands/clear_sessions.py
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone

class Command(BaseCommand):
    help = 'Clears all Django sessions to resolve authentication issues'

    def handle(self, *args, **options):
        # Delete all sessions
        num_deleted, _ = Session.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {num_deleted} sessions')
        )
        self.stdout.write(
            self.style.WARNING('Please log in again to create a new session with the correct user ID format.')
        )