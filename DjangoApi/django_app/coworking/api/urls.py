from django .urls import path ,include ,re_path 
from django .shortcuts import redirect 
from rest_framework .routers import DefaultRouter 

from .views import (
RegisterView ,EmailLoginView ,LogoutView ,MeView ,CsrfView ,
ReservationViewSet ,
ics_reservation ,ics_reservation_cancel ,
)


router =DefaultRouter ()
router .trailing_slash =r'/?'
router .register (r"reservations",ReservationViewSet ,basename ="reservation")

def _reservations_redirect (request ):

    qs =request .META .get ("QUERY_STRING")or ""
    return redirect ("/api/reservations/"+(f"?{qs}"if qs else ""),permanent =False )

urlpatterns =[

path ("auth/register",RegisterView .as_view (),name ="auth_register"),
path ("auth/login",EmailLoginView .as_view (),name ="auth_login"),
path ("auth/logout",LogoutView .as_view (),name ="auth_logout"),
path ("auth/me",MeView .as_view (),name ="auth_me"),
path ("auth/csrf",CsrfView .as_view (),name ="auth_csrf"),


path ("ics/reservations/<str:pk>.ics",ics_reservation ,name ="ics_reservation"),
path ("ics/reservations/<str:pk>/cancel.ics",ics_reservation_cancel ,name ="ics_reservation_cancel"),


re_path (r"^reservations$",_reservations_redirect ),


path ("",include (router .urls )),
]
