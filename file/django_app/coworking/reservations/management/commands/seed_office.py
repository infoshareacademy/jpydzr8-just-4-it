
from django.core.management.base import BaseCommand
from reservations.models import Floor, Zone, Desk

# Helper to add a desk
def add_desk(floor, zone, label, x, y, deep=False, dock=False, dual=False, adj=False):
    Desk.objects.get_or_create(
        floor=floor, zone=zone, label=label,
        defaults=dict(is_deep_work=deep, has_dock=dock, has_dual_monitors=dual,
                      has_adjustable_desk=adj, x_pct=x, y_pct=y)
    )

class Command(BaseCommand):
    help = "Seed floors with a designed layout matching PNG plan"

    def handle(self, *args, **opts):
        # ---------- FLOOR 4: 20 desks, 4 deep left, 16 open grouped by tables ----------
        f4, _ = Floor.objects.get_or_create(number=4)
        if f4.image_path != "floorplans/floor4_final.jpg":
            f4.image_path = "floorplans/floor4_final.jpg"
            f4.save(update_fields=["image_path"])
        # usuń poprzedni układ, żeby uniknąć zdublowanych biurek przy wielokrotnym seedowaniu
        Desk.objects.filter(floor=f4).delete()

        open_z4, _ = Zone.objects.get_or_create(floor=f4, name="Open Workspace", type="OPEN")
        deep_z4, _ = Zone.objects.get_or_create(floor=f4, name="Strefa Deep Work", type="DEEP")
        Zone.objects.get_or_create(floor=f4, name="Chill Room", type="CHILL")
        Zone.objects.get_or_create(floor=f4, name="Kuchnia", type="KITCH")

        # Deep Work (lewa strona, 4 pojedyncze stanowiska w alkowie)
        deep_positions = [(14,28),(18,32),(14,38),(18,42)]
        for i,(x,y) in enumerate(deep_positions, start=1):
            add_desk(f4, deep_z4, f"D{i}", x, y, deep=True, dock=True, dual=True, adj=True)

        # Open Workspace – grupy po 6 i 4 wokół stołów (na PNG)
        # zdefiniuj środki stołów (x%, y%) i rozkład 6 krzeseł dookoła
        def six_pack(cx, cy, label_prefix, start_index):
            # sześć siedzisk: lewo, prawo, góra, dół, lewo-góra, prawo-dół (delikatnie)
            offs = [(-3.5,0),(3.5,0),(0,-3),(0,3),(-2.8,-2.2),(2.8,2.2)]
            n = 0
            for dx,dy in offs:
                add_desk(f4, open_z4, f"{label_prefix}{start_index+n}", cx+dx, cy+dy,
                         dock=(n%2==0), dual=(n%3==0), adj=(n%2==1))
                n += 1
            return start_index+n

        def four_pack_long(cx, cy, label_prefix, start_index):
            # cztery siedziska długiego stołu (po bokach)
            offs = [(-3.8,0),(-1.2,0),(1.2,0),(3.8,0)]
            n=0
            for dx,dy in offs:
                add_desk(f4, open_z4, f"{label_prefix}{start_index+n}", cx+dx, cy+dy,
                         dock=(n%2==1), dual=(n%2==0), adj=(n==2))
                n+=1
            return start_index+n

        idx = 1
        # Górny rząd: trzy stoły (lewy zielony, środkowy pomarańczowy, prawy zielony)
        idx = six_pack(32,22,"O",idx)   # top-left group
        idx = four_pack_long(60,24,"O",idx)  # top-center long
        idx = six_pack(86,22,"O",idx)   # top-right group
        # Dół: długi pasek (4 miejsca) odtworzony dla coworkingu
        for dx in [-10, -3, 4, 11]:
            add_desk(f4, open_z4, f"O{idx}", 60+dx*0.6, 70, dock=(idx%2==0), dual=True, adj=False)
            idx += 1

        # ---------- Other floors quick-fill (kept from previous seed) ----------
        floor_images = {
            5: "floorplans/floor5.jpg",
            6: "floorplans/floor6.jpg",
            7: "floorplans/floor7_correct.jpg",
        }

        for n, open_cnt, deep_cnt in [(5,30,6),(6,25,5),(7,35,7)]:
            f,_=Floor.objects.get_or_create(number=n)
            desired_image = floor_images.get(n, f.image_path)
            if desired_image and f.image_path != desired_image:
                f.image_path = desired_image
                f.save(update_fields=["image_path"])
            Desk.objects.filter(floor=f).delete()
            open_z,_=Zone.objects.get_or_create(floor=f,name="Open Workspace",type="OPEN")
            deep_z,_=Zone.objects.get_or_create(floor=f,name="Deep Work",type="DEEP")
            # prosta siatka (bez PNG układu)
            import random
            xs_open=[55,60,65,70,75,80]; ys_open=[20,26,32,38,50,58,66,72]
            xs_deep=[20,28,36]; ys_deep=[24,32,40,48,56]
            def rp(xs,ys): return (random.choice(xs),random.choice(ys))
            for i in range(1,deep_cnt+1):
                x,y=rp(xs_deep,ys_deep)
                Desk.objects.get_or_create(floor=f,zone=deep_z,label=f"D{i}",
                    defaults=dict(is_deep_work=True,has_dock=True,has_dual_monitors=True,has_adjustable_desk=True,x_pct=x,y_pct=y))
            for i in range(1,open_cnt+1):
                x,y=rp(xs_open,ys_open)
                Desk.objects.get_or_create(floor=f,zone=open_z,label=f"O{i}",
                    defaults=dict(is_deep_work=False,has_dock=random.choice([True,False]),has_dual_monitors=random.choice([True,False]),has_adjustable_desk=random.choice([True,False]),x_pct=x,y_pct=y))

        self.stdout.write(self.style.SUCCESS("Seeded floor 4 with designed layout + floors 5/6/7."))
