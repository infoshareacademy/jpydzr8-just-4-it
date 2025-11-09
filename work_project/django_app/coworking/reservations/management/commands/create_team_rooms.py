from django.core.management.base import BaseCommand
from reservations.models import Floor, Zone, TeamRoom

class Command(BaseCommand):
    help = 'Tworzy przykładowe team rooms'

    def handle(self, *args, **options):
        # Pobierz piętra
        floor4 = Floor.objects.get(number=4)
        floor5 = Floor.objects.get(number=5)
        
        # Pobierz strefy
        try:
            deep_work_zone = Zone.objects.filter(type='DEEP').first()
            open_zone = Zone.objects.filter(type='OPEN').first()
        except:
            deep_work_zone = None
            open_zone = None
        
        # Utwórz team rooms
        team_rooms = [
            {
                'name': 'Sala konferencyjna A',
                'floor': floor4,
                'zone': open_zone,
                'capacity': 8,
                'description': 'Duża sala konferencyjna z projektorem i tablicą'
            },
            {
                'name': 'Sala spotkań B',
                'floor': floor4,
                'zone': open_zone,
                'capacity': 4,
                'description': 'Mniejsza sala do spotkań zespołowych'
            },
            {
                'name': 'Focus Room',
                'floor': floor5,
                'zone': deep_work_zone,
                'capacity': 2,
                'description': 'Cicha sala do pracy w parach'
            },
            {
                'name': 'Sala prezentacji',
                'floor': floor5,
                'zone': open_zone,
                'capacity': 12,
                'description': 'Duża sala z ekranem i systemem audio'
            }
        ]
        
        created_count = 0
        for room_data in team_rooms:
            room, created = TeamRoom.objects.get_or_create(
                name=room_data['name'],
                floor=room_data['floor'],
                defaults=room_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Utworzono: {room.name}')
            else:
                self.stdout.write(f'Już istnieje: {room.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Utworzono {created_count} nowych team rooms')
        )

