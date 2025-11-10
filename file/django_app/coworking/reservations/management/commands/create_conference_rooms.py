from django.core.management.base import BaseCommand
from reservations.models import Floor, ConferenceRoom

class Command(BaseCommand):
    help = 'Create sample conference rooms for each floor'

    def handle(self, *args, **options):
        floors = Floor.objects.all()
        
        conference_rooms_data = [
            {
                'name': 'Conference Room A',
                'capacity': 8,
                'description': 'Large conference room with modern equipment',
                'has_projector': True,
                'has_whiteboard': True,
                'has_video_conference': True
            },
            {
                'name': 'Conference Room B',
                'capacity': 6,
                'description': 'Medium-sized meeting room',
                'has_projector': True,
                'has_whiteboard': True,
                'has_video_conference': False
            },
            {
                'name': 'Meeting Room C',
                'capacity': 4,
                'description': 'Small meeting room for team discussions',
                'has_projector': False,
                'has_whiteboard': True,
                'has_video_conference': False
            },
            {
                'name': 'Boardroom',
                'capacity': 12,
                'description': 'Executive boardroom with premium features',
                'has_projector': True,
                'has_whiteboard': True,
                'has_video_conference': True
            }
        ]
        
        created_count = 0
        
        for floor in floors:
            for room_data in conference_rooms_data:
                room, created = ConferenceRoom.objects.get_or_create(
                    name=room_data['name'],
                    floor=floor,
                    defaults={
                        'capacity': room_data['capacity'],
                        'description': room_data['description'],
                        'has_projector': room_data['has_projector'],
                        'has_whiteboard': room_data['has_whiteboard'],
                        'has_video_conference': room_data['has_video_conference'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created conference room: {room.name} on Floor {floor.number}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Conference room already exists: {room.name} on Floor {floor.number}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} conference rooms')
        )
