from rest_framework_simplejwt .serializers import TokenObtainPairSerializer 
from django .contrib .auth import get_user_model 
from django .contrib .auth .hashers import check_password 

User =get_user_model ()

class EmailTokenObtainPairSerializer (TokenObtainPairSerializer ):
    username_field ='email'

    def validate (self ,attrs ):
        email =attrs .get ('email')
        password =attrs .get ('password')
        try :
            user =User .objects .get (email =email )
        except User .DoesNotExist :
            self .error_messages ['no_active_account']='Invalid credentials'
            raise self .raise_invalid_user ()
        if not user .is_active or not check_password (password ,user .password ):
            self .error_messages ['no_active_account']='Invalid credentials'
            raise self .raise_invalid_user ()
        data =super ().validate ({'email':email ,'password':password })
        return data 
