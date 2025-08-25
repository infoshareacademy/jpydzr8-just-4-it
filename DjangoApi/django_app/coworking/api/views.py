from datetime import datetime ,timedelta 

from django .contrib .auth import authenticate ,login ,logout ,get_user_model 
from django .db .models import Q 
from django .http import HttpResponse 
from django .middleware .csrf import get_token 
from django .views .decorators .csrf import ensure_csrf_cookie 
from django .views .decorators .http import require_GET 

from rest_framework import status ,viewsets ,permissions 
from rest_framework .response import Response 
from rest_framework .views import APIView 

from .models import Reservation 
from .serializers import ReservationSerializer 

User =get_user_model ()






class RegisterView (APIView ):
    permission_classes =[permissions .AllowAny ]

    def post (self ,request ):
        email =(request .data .get ("email")or "").strip ().lower ()
        password =request .data .get ("password")or ""
        name =request .data .get ("name")or request .data .get ("username")or ""
        if not email or not password :
            return Response ({"detail":"email and password are required"},status =400 )
        if User .objects .filter (Q (username =email )|Q (email =email )).exists ():
            return Response ({"detail":"User already exists"},status =400 )
        user =User .objects .create_user (username =email ,email =email ,password =password )
        if name :

            if hasattr (user ,"first_name"):
                user .first_name =name 
            user .save ()
        return Response ({"ok":True },status =201 )


class EmailLoginView (APIView ):
    permission_classes =[permissions .AllowAny ]

    def post (self ,request ):
        email =(request .data .get ("email")or request .data .get ("username")or "").strip ().lower ()
        password =request .data .get ("password")or ""
        if not email or not password :
            return Response ({"detail":"email and password are required"},status =400 )

        user =authenticate (request ,username =email ,password =password )
        if user is None :

            try :
                u =User .objects .get (email =email )
                user =authenticate (request ,username =u .username ,password =password )
            except User .DoesNotExist :
                user =None 
        if user is None :
            return Response ({"detail":"Invalid credentials"},status =400 )
        login (request ,user )
        return Response ({"ok":True })


class LogoutView (APIView ):
    def post (self ,request ):
        logout (request )
        return Response ({"ok":True })


class MeView (APIView ):
    def get (self ,request ):
        if not request .user .is_authenticated :
            return Response ({"authenticated":False },status =200 )
        u =request .user 
        return Response ({
        "authenticated":True ,
        "username":getattr (u ,"username",""),
        "email":getattr (u ,"email",""),
        "first_name":getattr (u ,"first_name",""),
        "last_name":getattr (u ,"last_name",""),
        })


class CsrfView (APIView ):
    permission_classes =[permissions .AllowAny ]

    @ensure_csrf_cookie 
    def get (self ,request ):
        token =get_token (request )

        return Response ({"csrfToken":token })






class ReservationViewSet (viewsets .ModelViewSet ):
    """Pełne CRUD na rezerwacjach (SQLite), autoryzacja po sesji Django."""
    permission_classes =[permissions .IsAuthenticated ]
    serializer_class =ReservationSerializer 
    lookup_field ="pk"

    def get_queryset (self ):
        qs =Reservation .objects .all ().order_by ("date","seat_id")
        df =self .request .query_params .get ("date_from")
        dt =self .request .query_params .get ("date_to")
        d_exact =self .request .query_params .get ("date")
        if d_exact :
            qs =qs .filter (date =d_exact )
        elif df and dt :

            qs =qs .filter (date__gte =df ,date__lte =dt )
        return qs 






def _ics_headers (filename :str )->dict :
    return {
    "Content-Type":"text/calendar; charset=utf-8",
    "Content-Disposition":f'attachment; filename="{filename}"',
    }

def _ics_escape (text :str )->str :

    s =(text or "")
    s =s .replace ("\\","\\\\")
    s =s .replace (",","\\,")
    s =s .replace (";","\\;")
    s =s .replace ("\r\n","\\n").replace ("\n","\\n").replace ("\r","\\n")
    return s 

def _ics_datetime (d :str )->datetime :

    try :
        return datetime .strptime (d ,"%Y-%m-%d")
    except Exception :
        return datetime .utcnow ()

@require_GET 
def ics_reservation (request ,pk :str ):
    """Return a single VEVENT (METHOD:PUBLISH) for Reservation pk as all-day event."""
    try :
        r =Reservation .objects .get (pk =pk )
    except Reservation .DoesNotExist :
        return HttpResponse ("Not found",status =404 )

    start =_ics_datetime (r .date )
    end =start +timedelta (days =1 )

    uid =f"{r.id}@coworking.local"
    summary =f"Seat {r.seat_id} — {getattr(r, 'name', '')}"
    desc =f"Email: {getattr(r, 'email', '')}\nNotes: {getattr(r, 'notes', '')}"

    lines =[
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Coworking App//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    f"UID:{_ics_escape(uid)}",
    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
    f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
    f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
    f"SUMMARY:{_ics_escape(summary)}",
    f"DESCRIPTION:{_ics_escape(desc)}",
    f"LOCATION:{_ics_escape(getattr(r, 'seat_id', ''))}",
    "END:VEVENT",
    "END:VCALENDAR",
    "",
    ]
    resp =HttpResponse ("\r\n".join (lines ))
    for k ,v in _ics_headers (f"{r.id}.ics").items ():
        resp [k ]=v 
    return resp 

@require_GET 
def ics_reservation_cancel (request ,pk :str ):
    """Return VEVENT with METHOD:CANCEL for Reservation pk (to remove in clients that honor CANCEL)."""
    try :
        r =Reservation .objects .get (pk =pk )
    except Reservation .DoesNotExist :

        class R :...
        r =R ()
        r .id =pk 
        r .date =datetime .utcnow ().strftime ("%Y-%m-%d")
        r .seat_id =""
        r .name =""
        r .email =""
        r .notes =""

    start =_ics_datetime (r .date )
    end =start +timedelta (days =1 )
    uid =f"{r.id}@coworking.local"

    lines =[
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Coworking App//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:CANCEL",
    "BEGIN:VEVENT",
    f"UID:{_ics_escape(uid)}",
    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
    f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
    f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
    "STATUS:CANCELLED",
    "END:VEVENT",
    "END:VCALENDAR",
    "",
    ]
    resp =HttpResponse ("\r\n".join (lines ))
    for k ,v in _ics_headers (f"{r.id}_cancel.ics").items ():
        resp [k ]=v 
    return resp 
