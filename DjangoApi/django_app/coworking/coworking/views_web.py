from django .views .generic import TemplateView 
from django .http import Http404 
from django .template .loader import get_template 

class AnyTemplateView (TemplateView ):
    template_name ='index.html'

    def get (self ,request ,page =None ,*args ,**kwargs ):

        if page :
            candidate =page if page .endswith ('.html')else f"{page}.html"
        else :
            candidate =self .template_name 
        try :

            get_template (candidate )
        except Exception :
            raise Http404 ("Page not found")
        self .template_name =candidate 
        return super ().get (request ,*args ,**kwargs )
