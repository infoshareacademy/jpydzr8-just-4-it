

import django .utils .timezone 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    initial =True 

    dependencies =[
    ('auth','0012_alter_user_first_name_max_length'),
    ]

    operations =[
    migrations .CreateModel (
    name ='User',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('password',models .CharField (max_length =128 ,verbose_name ='password')),
    ('last_login',models .DateTimeField (blank =True ,null =True ,verbose_name ='last login')),
    ('is_superuser',models .BooleanField (default =False ,help_text ='Designates that this user has all permissions without explicitly assigning them.',verbose_name ='superuser status')),
    ('email',models .EmailField (max_length =254 ,unique =True )),
    ('full_name',models .CharField (blank =True ,default ='',max_length =255 )),
    ('is_active',models .BooleanField (default =True )),
    ('is_staff',models .BooleanField (default =False )),
    ('created_at',models .DateTimeField (default =django .utils .timezone .now )),
    ('groups',models .ManyToManyField (blank =True ,help_text ='The groups this user belongs to. A user will get all permissions granted to each of their groups.',related_name ='user_set',related_query_name ='user',to ='auth.group',verbose_name ='groups')),
    ('user_permissions',models .ManyToManyField (blank =True ,help_text ='Specific permissions for this user.',related_name ='user_set',related_query_name ='user',to ='auth.permission',verbose_name ='user permissions')),
    ],
    options ={
    'abstract':False ,
    },
    ),
    migrations .CreateModel (
    name ='Reservation',
    fields =[
    ('id',models .CharField (max_length =64 ,primary_key =True ,serialize =False )),
    ('seat_id',models .CharField (db_index =True ,max_length =64 )),
    ('date',models .CharField (db_index =True ,max_length =10 )),
    ('name',models .CharField (max_length =255 )),
    ('email',models .CharField (max_length =255 )),
    ('notes',models .CharField (blank =True ,default ='',max_length =1024 )),
    ('created_at',models .DateTimeField (default =django .utils .timezone .now )),
    ],
    options ={
    'constraints':[models .UniqueConstraint (fields =('seat_id','date'),name ='uq_resv_seat_date')],
    },
    ),
    ]
