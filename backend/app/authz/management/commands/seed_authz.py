from app.authz.models import Permission, Role
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Seeds initial roles and permissions for AirPart ERP authz module.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('Seeding initial roles and permissions...')
        )

        # 1. ایجاد نقش Super Admin
        super_admin_role, created = Role.objects.get_or_create(
            name='SUPER_ADMIN',
            defaults={
                'description': (
                    'System-wide super administrator with full access.'
                )
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Created role: SUPER_ADMIN successfully.'
                )
            )
        else:
            self.stdout.write('Role SUPER_ADMIN already exists.')

        # 2. ایجاد مجوزهای پایه (مثلاً مدیریت قطعات هواپیما و هلیکوپتر)
        base_permissions = [
            {
                'code': 'parts:create',
                'name': 'Create Aircraft Part',
                'description': 'Can add new parts to inventory',
            },
            {
                'code': 'parts:read',
                'name': 'View Aircraft Part',
                'description': 'Can view parts inventory',
            },
            {
                'code': 'parts:update',
                'name': 'Update Aircraft Part',
                'description': 'Can modify part details',
            },
            {
                'code': 'parts:delete',
                'name': 'Delete Aircraft Part',
                'description': 'Can remove parts from system',
            },
        ]

        for perm_data in base_permissions:
            perm, p_created = Permission.objects.get_or_create(
                code=perm_data['code'], defaults=perm_data
            )
            if p_created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created permission: {perm.code}")
                )

        self.stdout.write(
            self.style.SUCCESS('Authz seeding completed successfully!')
        )
