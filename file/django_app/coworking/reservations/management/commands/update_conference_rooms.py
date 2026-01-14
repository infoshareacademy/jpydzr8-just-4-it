from django.core.management.base import BaseCommand
from reservations.models import Floor, ConferenceRoom

class Command(BaseCommand):
    help = 'Update conference rooms to have only one per floor'

    def handle(self, *args, **options):
        floors = Floor.objects.all()
        
        # Usuń wszystkie istniejące sal konferencyjne
        ConferenceRoom.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all existing conference rooms'))
        
        # Stwórz jedną salę konferencyjną na piętro
        for floor in floors:
            ConferenceRoom.objects.create(
                name=f'Conference Room - Floor {floor.number}',
                floor=floor,
                capacity=8,
                description=f'Main conference room on floor {floor.number} with modern equipment',
                has_projector=True,
                has_whiteboard=True,
                has_video_conference=True,
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created conference room on Floor {floor.number}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {floors.count()} conference rooms (one per floor)')
        )
