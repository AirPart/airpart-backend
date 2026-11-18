from django.core.management.base import BaseCommand

from accounts.models import User

DEMO_USERS = [
    ("alice", "branch_tehran", User.Role.SALES),
    ("bob", "branch_isfahan", User.Role.SALES),
    ("carol", "branch_tehran", User.Role.FINANCE),
]

DEMO_PASSWORD = "demo-pass-12345"


class Command(BaseCommand):
    help = "Create demo users matching authz/policy.csv (PoC only)."

    def handle(self, *args, **options):
        for username, domain, role in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"domain": domain, "role": role},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(f"created {username} ({role}@{domain})")
            else:
                self.stdout.write(f"skipped {username} (already exists)")
        self.stdout.write(self.style.SUCCESS(f"password for all demo users: {DEMO_PASSWORD}"))
