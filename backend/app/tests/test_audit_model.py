from django.test import TestCase

from app.accounts.models import AuthAuditLog
from django.contrib.auth import get_user_model


class AuthAuditLogModelTests(TestCase):
    def test_db_table_name(self):
        self.assertEqual(AuthAuditLog._meta.db_table, "auth_audit_logs")

    def test_composite_indexes(self):
        names = {idx.name for idx in AuthAuditLog._meta.indexes}
        self.assertEqual(names, {"audit_event_ts_idx", "audit_user_ts_idx"})

    def test_defaults_and_timestamp(self):
        log = AuthAuditLog.objects.create(event_type=AuthAuditLog.EventType.LOGIN_FAILED)
        self.assertIsNotNone(log.timestamp)
        self.assertIsNone(log.user)
        self.assertEqual(log.metadata, {})

    def test_user_deletion_keeps_log(self):
        user = get_user_model().objects.create_user(username="u1", password="x")
        log = AuthAuditLog.objects.create(
            event_type=AuthAuditLog.EventType.LOGIN_SUCCESS, user=user
        )
        user.delete()
        log.refresh_from_db()
        self.assertIsNone(log.user)

