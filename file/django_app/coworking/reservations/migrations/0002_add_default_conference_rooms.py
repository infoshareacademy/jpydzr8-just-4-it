from django.db import migrations


def create_conference_rooms(apps, schema_editor):
    Floor = apps.get_model('reservations', 'Floor')
    ConferenceRoom = apps.get_model('reservations', 'ConferenceRoom')
    Zone = apps.get_model('reservations', 'Zone')

    for floor in Floor.objects.all():
        if ConferenceRoom.objects.filter(floor=floor).exists():
            continue

        zone = Zone.objects.filter(floor=floor, type='CONF').first()
        room_name = f"F{floor.number} Konferencyjna"

        ConferenceRoom.objects.create(
            name=room_name,
            floor=floor,
            zone=zone,
            capacity=8,
            description="Domyślna sala konferencyjna dla piętra",
            has_projector=True,
            has_whiteboard=True,
            has_video_conference=True,
            is_active=True,
        )


def remove_conference_rooms(apps, schema_editor):
    ConferenceRoom = apps.get_model('reservations', 'ConferenceRoom')
    ConferenceRoom.objects.filter(
        description='Domyślna sala konferencyjna dla piętra'
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_conference_rooms, remove_conference_rooms),
    ]

