from django .urls import path ,include ,re_path 
from django .shortcuts import redirect 
from rest_framework .routers import DefaultRouter 
from .views import CsrfTokenView
from .views import (
    CsrfTokenView,
    LoginView,          
    RegisterView,
    LogoutView,
    MeView,
    ReservationViewSet, 
    ics_reservation,           
    ics_reservation_cancel,
)

from .views import CsrfTokenView, LoginView, RegisterView, LogoutView, MeView


router =DefaultRouter ()
router .trailing_slash =r'/?'
router .register (r"reservations",ReservationViewSet ,basename ="reservation")

def _reservations_redirect (request ):

    qs =request .META .get ("QUERY_STRING")or ""
    return redirect ("/api/reservations/"+(f"?{qs}"if qs else ""),permanent =False )

urlpatterns =[
path("auth/csrf", CsrfTokenView.as_view(), name="csrf"),
path ("auth/register",RegisterView.as_view (),name ="register"),
path ("auth/login",LoginView.as_view (),name ="login"),
path ("auth/logout",LogoutView.as_view (),name ="logout"),
path ("auth/me",MeView.as_view (),name ="me"),


path ("ics/reservations/<str:pk>.ics",ics_reservation ,name ="ics_reservation"),
path ("ics/reservations/<str:pk>/cancel.ics",ics_reservation_cancel ,name ="ics_reservation_cancel"),


re_path (r"^reservations$",_reservations_redirect ),


path ("",include (router .urls )),
]
