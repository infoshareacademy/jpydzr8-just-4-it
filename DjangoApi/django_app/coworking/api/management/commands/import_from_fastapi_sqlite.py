from django .core .management .base import BaseCommand ,CommandError 
from django .db import transaction 
from django .contrib .auth import get_user_model 
from api .models import Reservation 
import sqlite3 ,os 

User =get_user_model ()

class Command (BaseCommand ):
    help ='Import users and reservations from FastAPI SQLite (tables: users, reservations).'

    def add_arguments (self ,parser ):
        parser .add_argument ('--path',required =True ,help ='Path to FastAPI SQLite app.db')
        parser .add_argument ('--skip-users',action ='store_true')
        parser .add_argument ('--skip-reservations',action ='store_true')

    @transaction .atomic 
    def handle (self ,*args ,**opts ):
        path =opts ['path']
        if not os .path .exists (path ):
            raise CommandError (f'SQLite not found: {path}')
        con =sqlite3 .connect (path )
        cur =con .cursor ()

        if not opts ['skip-users']:
            try :
                cur .execute ('SELECT email, password_hash, full_name, is_active, is_superuser FROM users')
                rows =cur .fetchall ()
                for email ,password_hash ,full_name ,is_active ,is_superuser in rows :
                    user ,created =User .objects .get_or_create (email =email ,defaults ={
                    'full_name':full_name or '',
                    'is_active':bool (is_active ),
                    'is_superuser':bool (is_superuser ),
                    'is_staff':bool (is_superuser ),
                    })
                    if created :
                        user .set_unusable_password ()
                        user .save ()
                self .stdout .write (self .style .SUCCESS (f'Imported/ensured {len(rows)} users (passwords set unusable).'))
            except Exception as e :
                self .stderr .write (str (e ))
                raise CommandError ('Failed to import users')

        if not opts ['skip-reservations']:
            try :
                cur .execute ('SELECT id, seat_id, date, name, email, notes, created_at FROM reservations')
                rows =cur .fetchall ()
                for rid ,seat_id ,date ,name ,email ,notes ,created_at in rows :
                    Reservation .objects .get_or_create (id =rid ,defaults ={
                    'seat_id':seat_id ,'date':date ,'name':name ,'email':email ,
                    'notes':notes or ''
                    })
                self .stdout .write (self .style .SUCCESS (f'Imported {len(rows)} reservations.'))
            except Exception as e :
                self .stderr .write (str (e ))
                raise CommandError ('Failed to import reservations')

        con .close ()
