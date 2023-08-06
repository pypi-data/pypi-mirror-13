from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_static import static
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns 
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext 
from django.http import HttpResponseRedirect
from django.http import Http404

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.core.admin import DisplayableAdmin
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from happystamp.models import Merchant, GCMNotification
from happystamp.models import UserPreferences
from happystamp.models import PushNotification
from happystamp.models import Program
from happystamp.models import ProgramStep
from happystamp.models import Card
from happystamp.models import Transaction
from happystamp.models import mCustomer
from happystamp.models import mMerchant
from happystamp.models import mProgram
from happystamp.models import mCard
from happystamp.models import mPushNotification
from happystamp.models import GCMDevice
from happystamp.models import new_customer

###############################################################################
#                               mCustomerAdmin                                #
###############################################################################
class mCustomerAdmin(ModelAdmin):
    list_display = ("email", "first_name", "last_name", "date_joined",)
    
    fieldsets = (
        (None,
            {"fields": ("first_name", "last_name", "email",)}),               
    )

###############################################################################
#                               mMerchantAdmin                                #
###############################################################################
class mMerchantAdmin(ModelAdmin):
    class Media:
        css = {"all": (static("css/admin/mmerchant.css"),)}
        
    list_display = ("name", "email", )
    list_filter = ("name", )
    fieldsets = (
        (_("Store Information"),
            {"fields": ("name", "brand_logo", "content",)}),  
        (_("Contact Information"),
            {"fields": ("email", "address", "phone",)}),
             
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content'].label = _("Business Description")        
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.user = request.user            
        obj.save()
    
###############################################################################
#                               mProgramAdmin                                 #
###############################################################################        
class ProgramStepInline(TabularDynamicInlineAdmin):
    fieldsets = (
        (None,
            {"fields": ("redeem", "reward", "reward_logo" )}),  
    )
    model = ProgramStep    
    
class mProgramAdmin(DisplayableAdmin):
    class Media:
        css = {"all": (static("css/admin/mprogram.css"),)}

    view_on_site = False    
    list_display = ("title", "merchant", "status",)
    list_editable = ()
    inlines = (ProgramStepInline,)
    fieldsets = (
        (_("Program Information"),
            {"fields": ("merchant", "title", "status", "program_logo", "content",)}),                 
    )

    preview_template = 'admin/happystamp/mprogram/preview_form.html'
    qrcodes_template = 'admin/happystamp/mprogram/qrcodes_form.html'
    
    def get_urls(self):
        urls = super(mProgramAdmin, self).get_urls()
        my_urls = patterns('',
            (r'(?P<id>\d+)/preview$', self.admin_site.admin_view(self.preview)),
            (r'(?P<id>\d+)/qrcodes$', self.admin_site.admin_view(self.qrcodes)),
        )
        return my_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['title'].label = _("Program Title")        
        form.base_fields['content'].label = _("Program Description")
        return form
    
    def preview(self, request, id):
        program = Program.objects.get(pk=id)
                
        return render_to_response(self.preview_template, {
            'title': 'App Preview : %s' % program.title,
            'merchant': program.merchant,
            'steps': program.steps.all(),
            'program': program,             
            'opts': self.model._meta,  
            'is_popup': False          
        }, context_instance=RequestContext(request))

    def qrcodes(self, request, id):
        program = Program.objects.get(pk=id)
                
        return render_to_response(self.qrcodes_template, {
            'title': 'QR Codes : %s' % program.title,
            'merchant': program.merchant,
            'steps': program.steps.all(),
            'program': program,             
            'opts': self.model._meta,  
            'is_popup': False          
        }, context_instance=RequestContext(request))
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status==CONTENT_STATUS_PUBLISHED:
            return self.readonly_fields + ('status',)
        
        return self.readonly_fields
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)   
     
###############################################################################
#                               mCardAdmin                                    #
###############################################################################             
class TransactionInline(TabularDynamicInlineAdmin):    
    fieldsets = (
        (None,
            {"fields": ("created", "credit", "debit", "detail",)}),  
    )
    
    readonly_fields = ('created', 'credit', "debit", "detail",)

    model = Transaction
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class mCardForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255,
                                 widget=forms.TextInput(attrs={'class': "vTextField"}),)
    last_name = forms.CharField(max_length=255,
                                widget=forms.TextInput(attrs={'class': "vTextField"}),)
    email = forms.EmailField(max_length=255,
                             widget=forms.TextInput(attrs={'class': "vTextField"}),)          
    
    def clean(self):
        cleaned_data = super().clean()
        
        #Check the owner
        owner = mCustomer.objects.filter(email=cleaned_data.get('email', None)).first()        
        if owner is None:
            cleaned_data['new_customer'] = True            
            owner = mCustomer(first_name=cleaned_data.get('first_name', None),
                              last_name=cleaned_data.get('last_name', None),
                              email=cleaned_data.get('email', None))
            owner.save()            
        else:
            if mCard.objects.filter(owner_id=owner.id).count()>0:
                raise ValidationError(_("Already Enrolled"))
        
        cleaned_data['owner'] = owner
        
        return cleaned_data

    def _post_clean(self):
        super()._post_clean()
        self.instance.owner =  self.cleaned_data.get('owner', None)
        if self.cleaned_data.get('new_customer', None):
            setattr(self.instance, 'new_customer', True)
        
    class Meta:
        model = mCard
        fields = ("program", )
                        
class mCardAdmin(ModelAdmin):
    class Media:
        css = {"all": (static("css/admin/mcard.css"),)}
               
    list_display = ("owner", "program", "effective_date", "credit", )
    search_fields = ['owner__email']
    inlines = (TransactionInline, )
    
    def get_urls(self):
        urls = super(mCardAdmin, self).get_urls()
        my_urls = patterns('',
            (r'(?P<id>\d+)/redeem$', self.admin_site.admin_view(self.redeem)),
            (r'(?P<id>\d+)/reward$', self.admin_site.admin_view(self.reward)),            
        )
        return my_urls + urls
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ("owner", "program", 
                                           "effective_date", "credit")
        else:
            return self.readonly_fields + ("effective_date", "credit")
        
        return self.readonly_fields
    
    def get_inline_instances(self, request, obj=None):
        if obj is not None: 
            return super().get_inline_instances(request, obj)
        
        return []
        
    def get_fieldsets(self, request, obj=None):
        if obj is not None: 
            return ((None,
                     {"fields": ("owner", "program", "effective_date",)}),)
        return ((None,
                 {"fields": ("first_name", "last_name", "email", "program",)}),)
   
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None: 
            return super().get_form(request, obj, **kwargs)
        
        return mCardForm     
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = {}
        context.update(extra_context or {})
        obj = get_object_or_404(Card, id=object_id)
        context.update({'card': obj,
                        'rewards' : obj.get_eligible_rewards,
                        'can_redeem' : obj.can_redeem()})
        return self.changeform_view(request, object_id, form_url, context)
    
    def log_addition(self, request, object):
        super().log_addition(request, object)
        
        if getattr(object, 'new_customer'):
            #send new_customer signal
            new_customer.send(sender=self.__class__, instance=object.owner)
    
    def redeem(self, request, id):
        card = Card.objects.get(pk=id)
        if card:
            if card.can_redeem():
                card.redeem()
            else:
                raise Http404('Not authorized')        
            return HttpResponseRedirect("./");
        else:
            raise Http404('Not authorized')   
    
    def reward(self, request, id):    
        card = get_object_or_404(Card, id=id)                        
        program_step = get_object_or_404(ProgramStep, id = request.POST['step'], 
                                     program__pk=card.program.id)
        
        if card.can_reward(program_step):
            card.reward(program_step)
            return HttpResponseRedirect("./");
        else:
            raise Http404('Not authorized')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)
    
###############################################################################
#                          mPushNotificationAdmin                             #
###############################################################################         
class mPushNotificationAdmin(DisplayableAdmin):    
    list_display = ("title", "status",)
    list_editable = ()
    fieldsets = (
        (None,
            {"fields": ("title", "content",)}),                 
    )    

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content'].label = _("Message")
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.user = request.user 
            obj.status = CONTENT_STATUS_PUBLISHED           
        obj.save()
    
###############################################################################
#                           Merchant Admin Views                              #
###############################################################################    
#admin.site.register(mCustomer, mCustomerAdmin)
admin.site.register(mMerchant, mMerchantAdmin)
admin.site.register(mProgram, mProgramAdmin)
admin.site.register(mCard, mCardAdmin)
admin.site.register(mPushNotification, mPushNotificationAdmin)

###############################################################################
#                                  Admin Views                                #
############################################################################### 
admin.site.register(Merchant)
admin.site.register(Program)
admin.site.register(Card)
admin.site.register(PushNotification)
admin.site.register(UserPreferences)
admin.site.register(GCMDevice)
admin.site.register(GCMNotification)


