# Generated migration for initial data
from django.db import migrations


def create_initial_data(apps, schema_editor):
    """Tworzy podstawowe dane: piętra, strefy i stanowiska"""
    Floor = apps.get_model('reservations', 'Floor')
    Zone = apps.get_model('reservations', 'Zone')
    Desk = apps.get_model('reservations', 'Desk')
    ConferenceRoom = apps.get_model('reservations', 'ConferenceRoom')
    
    # Helper do dodawania stanowisk
    def add_desk(floor, zone, label, x, y, deep=False, dock=False, dual=False, adj=False):
        Desk.objects.get_or_create(
            floor=floor, 
            label=label,
            defaults={
                'zone': zone,
                'is_deep_work': deep, 
                'has_dock': dock, 
                'has_dual_monitors': dual,
                'has_adjustable_desk': adj, 
                'x_pct': x, 
                'y_pct': y
            }
        )
    
    # ---------- FLOOR 4: 20 stanowisk, 4 deep left, 16 open grouped by tables ----------
    f4, _ = Floor.objects.get_or_create(
        number=4,
        defaults={'image_path': 'floorplans/floor4_final.jpg'}
    )
    if f4.image_path != "floorplans/floor4_final.jpg":
        f4.image_path = "floorplans/floor4_final.jpg"
        f4.save(update_fields=["image_path"])
    
    # Usuń poprzednie stanowiska jeśli istnieją (dla idempotentności)
    Desk.objects.filter(floor=f4).delete()
    
    open_z4, _ = Zone.objects.get_or_create(floor=f4, name="Open Workspace", type="OPEN")
    deep_z4, _ = Zone.objects.get_or_create(floor=f4, name="Strefa Deep Work", type="DEEP")
    Zone.objects.get_or_create(floor=f4, name="Chill Room", type="CHILL")
    Zone.objects.get_or_create(floor=f4, name="Kuchnia", type="KITCH")
    
    # Deep Work (lewa strona, 4 pojedyncze stanowiska w alkowie)
    deep_positions = [(14, 28), (18, 32), (14, 38), (18, 42)]
    for i, (x, y) in enumerate(deep_positions, start=1):
        add_desk(f4, deep_z4, f"D{i}", x, y, deep=True, dock=True, dual=True, adj=True)
    
    # Open Workspace – grupy po 6 i 4 wokół stołów
    def six_pack(cx, cy, label_prefix, start_index):
        offs = [(-3.5, 0), (3.5, 0), (0, -3), (0, 3), (-2.8, -2.2), (2.8, 2.2)]
        n = 0
        for dx, dy in offs:
            add_desk(f4, open_z4, f"{label_prefix}{start_index+n}", cx+dx, cy+dy,
                     dock=(n%2==0), dual=(n%3==0), adj=(n%2==1))
            n += 1
        return start_index+n
    
    def four_pack_long(cx, cy, label_prefix, start_index):
        offs = [(-3.8, 0), (-1.2, 0), (1.2, 0), (3.8, 0)]
        n = 0
        for dx, dy in offs:
            add_desk(f4, open_z4, f"{label_prefix}{start_index+n}", cx+dx, cy+dy,
                     dock=(n%2==1), dual=(n%2==0), adj=(n==2))
            n += 1
        return start_index+n
    
    idx = 1
    # Górny rząd: trzy stoły
    idx = six_pack(32, 22, "O", idx)
    idx = four_pack_long(60, 24, "O", idx)
    idx = six_pack(86, 22, "O", idx)
    # Dół: długi pasek (4 miejsca)
    for dx in [-10, -3, 4, 11]:
        add_desk(f4, open_z4, f"O{idx}", 60+dx*0.6, 70, dock=(idx%2==0), dual=True, adj=False)
        idx += 1
    
    # ---------- Other floors: 5, 6, 7 ----------
    floor_images = {
        5: "floorplans/floor5.jpg",
        6: "floorplans/floor6.jpg",
        7: "floorplans/floor7_correct.jpg",
    }
    
    import random
    random.seed(42)  # Dla powtarzalności
    
    for n, open_cnt, deep_cnt in [(5, 30, 6), (6, 25, 5), (7, 35, 7)]:
        f, _ = Floor.objects.get_or_create(
            number=n,
            defaults={'image_path': floor_images.get(n, 'floorplans/floor4.png')}
        )
        desired_image = floor_images.get(n, f.image_path)
        if desired_image and f.image_path != desired_image:
            f.image_path = desired_image
            f.save(update_fields=["image_path"])
        
        # Usuń poprzednie stanowiska
        Desk.objects.filter(floor=f).delete()
        
        open_z, _ = Zone.objects.get_or_create(floor=f, name="Open Workspace", type="OPEN")
        deep_z, _ = Zone.objects.get_or_create(floor=f, name="Deep Work", type="DEEP")
        Zone.objects.get_or_create(floor=f, name="Chill Room", type="CHILL")
        Zone.objects.get_or_create(floor=f, name="Kuchnia", type="KITCH")
        
        # Prosta siatka
        xs_open = [55, 60, 65, 70, 75, 80]
        ys_open = [20, 26, 32, 38, 50, 58, 66, 72]
        xs_deep = [20, 28, 36]
        ys_deep = [24, 32, 40, 48, 56]
        
        def rp(xs, ys):
            return (random.choice(xs), random.choice(ys))
        
        for i in range(1, deep_cnt + 1):
            x, y = rp(xs_deep, ys_deep)
            Desk.objects.get_or_create(
                floor=f, 
                zone=deep_z, 
                label=f"D{i}",
                defaults={
                    'is_deep_work': True,
                    'has_dock': True,
                    'has_dual_monitors': True,
                    'has_adjustable_desk': True,
                    'x_pct': x,
                    'y_pct': y
                }
            )
        
        for i in range(1, open_cnt + 1):
            x, y = rp(xs_open, ys_open)
            Desk.objects.get_or_create(
                floor=f, 
                zone=open_z, 
                label=f"O{i}",
                defaults={
                    'is_deep_work': False,
                    'has_dock': random.choice([True, False]),
                    'has_dual_monitors': random.choice([True, False]),
                    'has_adjustable_desk': random.choice([True, False]),
                    'x_pct': x,
                    'y_pct': y
                }
            )
    
    # Utwórz sale konferencyjne dla każdego piętra (jeśli jeszcze nie istnieją)
    for floor in Floor.objects.all():
        if not ConferenceRoom.objects.filter(floor=floor).exists():
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


def remove_initial_data(apps, schema_editor):
    """Usuwa dane utworzone przez create_initial_data"""
    Floor = apps.get_model('reservations', 'Floor')
    Desk = apps.get_model('reservations', 'Desk')
    Zone = apps.get_model('reservations', 'Zone')
    ConferenceRoom = apps.get_model('reservations', 'ConferenceRoom')
    
    # Usuń sale konferencyjne utworzone przez migrację
    ConferenceRoom.objects.filter(
        description='Domyślna sala konferencyjna dla piętra'
    ).delete()
    
    # Usuń stanowiska
    Desk.objects.filter(floor__number__in=[4, 5, 6, 7]).delete()
    
    # Usuń strefy
    Zone.objects.filter(floor__number__in=[4, 5, 6, 7]).delete()
    
    # Usuń piętra
    Floor.objects.filter(number__in=[4, 5, 6, 7]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_add_default_conference_rooms'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, remove_initial_data),
    ]

