from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    help = "Safely reset demo data: remove users (except admin) and clear reservations. Use --yes to execute."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-email",
            type=str,
            default="admin@coworking.com",
            help="Email to keep (default: admin@coworking.com)",
        )
        parser.add_argument(
            "--users",
            action="store_true",
            help="Delete users except the kept one (and any superusers)",
        )
        parser.add_argument(
            "--reservations",
            action="store_true",
            help="Delete all reservation-related data (reservations, recurring, group, waitlist, conference, notifications, locks, subscriptions)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Execute without interactive confirmation",
        )

    def handle(self, *args, **options):
        keep_email = (options.get("keep_email") or "admin@coworking.com").strip().lower()
        do_users = options.get("users", False)
        do_res = options.get("reservations", False)
        assume_yes = options.get("yes", False)

        if not (do_users or do_res):
            self.stdout.write(self.style.WARNING("Nothing to do. Pass --users and/or --reservations."))
            return

        User = get_user_model()

        with transaction.atomic():
            if do_users:
                # Determine users to delete: all except the kept email and superusers/staff
                qs = User.objects.all()
                to_delete = qs.exclude(email__iexact=keep_email).exclude(is_superuser=True)
                count_users = to_delete.count()
            else:
                count_users = 0

            if do_res:
                # Collect models from reservations app
                from reservations.models import (
                    Reservation,
                    RecurringReservation,
                    GroupReservation,
                    Waitlist,
                    ConferenceReservation,
                    Notification,
                    DeskBookingLock,
                    NotificationSubscription,
                )
                res_counts = {
                    "Reservation": Reservation.objects.count(),
                    "RecurringReservation": RecurringReservation.objects.count(),
                    "GroupReservation": GroupReservation.objects.count(),
                    "Waitlist": Waitlist.objects.count(),
                    "ConferenceReservation": ConferenceReservation.objects.count(),
                    "Notification": Notification.objects.count(),
                    "DeskBookingLock": DeskBookingLock.objects.count(),
                    "NotificationSubscription": NotificationSubscription.objects.count(),
                }
                # API legacy Reservation (if present)
                api_res_count = 0
                try:
                    from api.models import Reservation as ApiReservation  # type: ignore
                    api_res_count = ApiReservation.objects.count()
                except Exception:
                    ApiReservation = None  # type: ignore
            else:
                res_counts = {}
                api_res_count = 0
                ApiReservation = None  # type: ignore

            # Summary
            self.stdout.write(self.style.NOTICE("Planned actions:"))
            if do_users:
                self.stdout.write(f"- Delete users (except '{keep_email}' and superusers): {count_users}")
            if do_res:
                for k, v in res_counts.items():
                    self.stdout.write(f"- Delete all {k}: {v}")
                if api_res_count:
                    self.stdout.write(f"- Delete API Reservation: {api_res_count}")

            if not assume_yes:
                self.stdout.write(self.style.WARNING("Dry-run only. Re-run with --yes to execute."))
                return

            # Execute
            if do_res:
                # Delete child/related models first to avoid FK issues
                NotificationSubscription.objects.all().delete()
                DeskBookingLock.objects.all().delete()
                Notification.objects.all().delete()
                Waitlist.objects.all().delete()
                GroupReservation.objects.all().delete()
                RecurringReservation.objects.all().delete()
                ConferenceReservation.objects.all().delete()
                Reservation.objects.all().delete()
                if ApiReservation:
                    ApiReservation.objects.all().delete()

            if do_users:
                # Keep kept email and all superusers
                to_delete.delete()

            self.stdout.write(self.style.SUCCESS("Data reset completed successfully."))




