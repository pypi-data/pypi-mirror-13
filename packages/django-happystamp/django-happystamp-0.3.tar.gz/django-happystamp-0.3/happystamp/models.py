import json
import datetime

from django.db import models
from django.db import transaction
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models.signals import ModelSignal

from mezzanine.core.models import Displayable
from mezzanine.core.models import RichText
from mezzanine.core.models import Ownable
from mezzanine.core.models import TimeStamped
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from html2text import html2text

from happystamp.util import generate_key
from happystamp.util import generate_form
from happystamp.util import generate_reward_form

from happystamp.util import app_sticker_template
from happystamp.util import redeem_card_template
from happystamp.util import reward_card_template

from happystamp.gcm import GCMMessage
from happystamp.gcm import post_push

new_customer = ModelSignal(providing_args=["instance"])

def upload_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

###############################################################################
#                              Customer                                       #
###############################################################################
class mCustomer(User):
    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("My Customers")
        proxy = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.username = self.email
            self.set_unusable_password()
            
        super(mCustomer, self).save(*args, **kwargs)

            
###############################################################################
#                              Merchant                                       #
###############################################################################
class Merchant(Ownable, RichText, TimeStamped):    
    name = models.CharField(_("Business Name"), max_length=255) 
    email = models.EmailField(_("Email"), max_length=255)
    address = models.CharField(_("Address"), max_length=255)
    phone = models.CharField(_("Phone #"), max_length=255)
    
    #brand logo
    brand_logo = ImageField(_("Brand Logo"),
                            upload_to=upload_directory_path)    
    
    class Meta:
        verbose_name = _("Merchant")
        verbose_name_plural = _("Merchants")
    
    def __str__(self):
        return self.name

class mMerchant(Merchant):
    class Meta:
        verbose_name = _("Merchant")
        verbose_name_plural = _("My Merchants")
        proxy = True
            
###############################################################################
#                              Program                                        #
###############################################################################    
class Link(object):
    def __init__(self, program='', key='', step='', action=''):
        self.program = program
        self.key = key
        self.step = step
        self.action = action
        
    def serialize(self):
        return json.dumps(self.__dict__).replace('program', 'id')        
             
class Program(Displayable, Ownable, RichText):
    #Enroll key 
    enroll_key = models.CharField(max_length=255)
    #Credit Key
    redeem_key = models.CharField(max_length=255)
    #Debit Key
    reward_key = models.CharField(max_length=255)
    #merchant link
    merchant = models.ForeignKey(Merchant)
    #Logo
    program_logo = ImageField(_("Program Logo"), 
                             upload_to=upload_directory_path)
    
    class Meta:
        verbose_name = _("Program")
        verbose_name_plural = _("Programs")

    def save(self, *args, **kwargs):
        if not self.id:
            self.user = self.merchant.user
            self.enroll_key = generate_key()
            self.redeem_key = generate_key()
            self.reward_key = generate_key()

        super(Program, self).save(*args, **kwargs)
    
    def is_published(self):
        return self.status == CONTENT_STATUS_PUBLISHED
        
    def can_enroll(self):
        return self.is_published()
    
    def enroll(self, owner):   
        mowner = mCustomer.objects.filter(pk=owner.id).first()     
        card = Card(owner=mowner, program=self) 
        card.save()
        return card
        
    @property
    def enroll_rq_url(self):
        link = Link(self.id, self.enroll_key, action='ENROLL').serialize() 
        return generate_form(link, 7, 1, app_sticker_template, 440, 465, 220, 220)
        
    @property
    def redeem_rq_url(self):
        link = Link(self.id, self.redeem_key, action='REDEEM').serialize()
        return generate_form(link, 4, 2, redeem_card_template, 312, 4, 130, 130)    
    
    @property
    def nb_steps(self):
        return self.steps.all().count()
    
    @property
    def nb_points(self):
        return self.steps.last().redeem
        
    def __str__(self):
        return str(self.title) + ', ' + str(self.merchant) 

class mProgram(Program):
    class Meta:
        verbose_name = _("Program")
        verbose_name_plural = _("My Programs")
        proxy = True
        
###############################################################################
#                              Program Step                                   #
###############################################################################    
class ProgramStep(Ownable, TimeStamped):
    #points redeemed
    redeem =  models.IntegerField()
    #reward description
    reward = models.CharField(_("Reward"), max_length=100)   
    #reward logo
    reward_logo = ImageField(_("Reward Logo"),
                             upload_to=upload_directory_path)  
    #reward passcode
    reward_passcode = models.CharField(max_length=255)
    #program
    program = models.ForeignKey(Program, related_name='steps', null=False)
    
    class Meta:
        verbose_name = _("Program Step")
        verbose_name_plural = _("Program Steps")
            
    @property
    def reward_rq_url(self):
        link = Link(self.program.id, self.program.reward_key, str(self.id) + '-' + self.reward_passcode, 'REWARD').serialize()
        return generate_reward_form(link, self.reward, self.reward_passcode, 4, 2, 
                                    reward_card_template,  312, 4, 130, 130)
     
    def save(self, *args, **kwargs):
        if not self.id:
            self.reward_passcode = generate_key()    
            self.user = self.program.user       

        super(ProgramStep, self).save(*args, **kwargs)
         
    def __str__(self):
        return str(self.program) + ', ' + str(self.redeem) 

###############################################################################
#                              Card                                           #
###############################################################################    
class Card(Ownable, TimeStamped):  
    owner = models.ForeignKey(mCustomer, verbose_name=_("Owner"),
                              related_name="%(class)s_owner")      
    #dates
    effective_date = models.DateField(_("Effective Date"), default=datetime.date.today())
    end_date = models.DateField(_("Expiration Date"), null=True, blank=True)
    cycle_start_date = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now())
    #credit
    credit = models.IntegerField(_("Balance"), default=0)
    #program link
    program = models.ForeignKey(Program, verbose_name=_("Program"))    

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")
    
    def qs_transactions(self):
        return self.transactions.filter(created__gte=self.cycle_start_date)
            
    @property
    def active_transactions(self):
        if self.cycle_start_date is not None:
            qs = self.qs_transactions()
            qs = qs.order_by('created')
            return list(qs.all())
                    
        return []
        
    @property
    def reward_transactions(self):
        if self.cycle_start_date is not None:
            qs = self.qs_transactions()
            qs = qs.filter(debit__gt=0).order_by('created')
            return list(qs.all())
        
        return []
    
    @property
    def redeem_transactions(self):
        if self.cycle_start_date is not None:
            qs = self.qs_transactions()
            qs = qs.filter(credit__gt=0).order_by('created')
            return list(qs.all())
        
        return []
    
    @property
    def is_all_rewarded(self):
        return self.program.nb_steps == len(self.reward_transactions)
    
    @property
    def is_all_redeemed(self):
        return len(self.redeem_transactions) == self.program.nb_points
    
    @property
    def balance(self):
        cur_balance = 0
        for tr in self.reward_transactions:
            if tr.debit > cur_balance: 
                cur_balance = tr.debit
                
        return len(self.redeem_transactions) - cur_balance
    
    def can_redeem(self, credit=1):
        if self.program.is_published():
            return not self.is_all_redeemed or self.is_all_rewarded
        
        return False
    
    def redeem(self, detail=_('Redeem')):                
        tr = Transaction(card=self,                                  
                         credit=1,
                         debit=0,
                         detail=detail)

        with transaction.atomic():
            tr.save()
            self.credit += tr.credit
            
            if self.credit > self.program.nb_points:
                self.credit = self.program.nb_points
                
            if self.is_all_rewarded: 
                self.cycle_start_date = tr.created 
                self.credit = tr.credit
            self.save()
        
        return tr
    
    def already_delivered(self, program_step):
        for tr in self.reward_transactions:
            if tr.debit == program_step.redeem:
                return True
                        
        return False
    
    def can_reward(self, program_step):
        if self.program.is_published():
            if self.credit >= program_step.redeem:
                return not self.already_delivered(program_step)
            
        return False
    
    def reward(self, program_step, detail=None):
        if detail is None:
            tr_detail = program_step.reward
        else:
            tr_detail = detail 
            
        tr = Transaction(card=self,                                  
                         credit=0,
                         debit=program_step.redeem,
                         detail=tr_detail)
        
        with transaction.atomic():
            tr.save()            
                 
        return tr                
    
    
    def get_eligible_rewards(self):
        steps = []
        for program_step in self.program.steps.all():
            if self.can_reward(program_step):
                steps.append(program_step)
        
        return steps

    def save(self, *args, **kwargs):
        if not self.id:
            self.user = self.program.user       

        super(Card, self).save(*args, **kwargs)
                
    def __str__(self):
        return str(self.user) + ', ' + str(self.program)

class mCard(Card):
    class Meta:
        proxy = True
        verbose_name = _("Card")
        verbose_name_plural = _("My Cards")
        
###############################################################################
#                              Transaction                                    #
###############################################################################  
class Transaction(Ownable, TimeStamped):    
    #transaction credit vs debit
    credit = models.IntegerField(_("Credit"))
    debit = models.IntegerField(_("Debit"))
    #transaction details
    detail = models.CharField(_("Detail"), max_length=255)
    #card link    
    card = models.ForeignKey(Card, related_name='transactions')

    class Meta:        
        ordering = ['-updated']
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
    
    @property
    def transaction_type(self):
        if self.credit > 0:
            return _("Redeem")
        
        return _("Reward")
    
    @property
    def details(self):
        if self.debit > 0:
            return self.detail        
        return ""
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.user = self.card.user       

        super(Transaction, self).save(*args, **kwargs)
            
    def __str__(self):
        return str(self.id) + ', ' + str(self.card)


###############################################################################
#                              User preferences                               #
###############################################################################
class UserPreferences(Ownable, TimeStamped):
    #Notification by email
    notif_email =  models.BooleanField(_("Email Notification"), default=True)   
    #Notification by push
    notif_push  =  models.BooleanField(_("Push Notification"), default=True)

    class Meta:        
        verbose_name = _("User Preferences")
        verbose_name_plural = _("User Preferences")
                
    def __str__(self):
        return _("Preference For ") + str(self.user)
    

###############################################################################
#                                 Notification                                #
###############################################################################
class PushNotification(Displayable, Ownable, RichText):
    class Meta:        
        ordering = ['-updated']
        verbose_name = _("Push Notifications")
        verbose_name_plural = _("Push Notifications")
    
    def __str__(self):
        return str(self.id)
    
    @property
    def text_content(self):
        return html2text(self.content)

class mPushNotification(PushNotification):
    class Meta:
        ordering = ['-updated']
        verbose_name = _("Push Notification")
        verbose_name_plural = _("My Push Notifications")
        proxy = True

###############################################################################
#                               Android Device                                #
###############################################################################
class DeviceManager(models.Manager):
    def get_devices(self, customer):
        try:
            user_prefs = UserPreferences.objects.filter(user__pk=customer.id, 
                                                        notif_push=True).first()
            if user_prefs is not None and user_prefs.notif_push: 
                return self.filter(user__pk=customer.id).filter(is_active=True)
        except Exception:
            pass
        
        return []
    
    def push_notification(self, notification):
        cards = Card.objects.filter(user__pk=notification.user.id)
        for card in cards:
            devices = self.get_devices(card.owner)
            for device in devices:
                device.send_message(notification.text_content, 
                                    notification=notification,
                                    merchant=card.program.merchant)
    
    
class GCMDevice(Ownable, TimeStamped):
    dev_id = models.CharField(verbose_name=_("Device ID"), max_length=50, unique=True,)
    reg_id = models.CharField(verbose_name=_("Registration ID"), max_length=255, unique=True)
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True, null=True)
    is_active = models.BooleanField(verbose_name=_("Is Active?"), default=True)

    objects = DeviceManager()
    
    def __str__(self):
        return self.dev_id

    class Meta:        
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ['-updated']
    
    def send_message(self, data, **kwargs):
        return GCMMessage().send(regs_id=[self.reg_id], data=data, **kwargs)

    def mark_inactive(self, **kwargs):
        self.is_active = False
        self.save()

class GCMNotification(Ownable, TimeStamped):
    #device link    
    device = models.ForeignKey(GCMDevice)
    #notification link
    notification = models.ForeignKey(PushNotification)
    #merchant link
    merchant = models.ForeignKey(Merchant, null=True)


@receiver(post_save, sender=mPushNotification)
def push_notification(sender,instance, signal, created, **kwargs):
    return created and GCMDevice.objects.push_notification(instance)       

@receiver(post_push, sender=GCMMessage)
def notify_push_done(sender, message, reg_id, error, **kwargs):
    device = GCMDevice.objects.filter(reg_id=reg_id).first()
    if error:        
        device.mark_inactive()
    else:
        gcm_notification = GCMNotification(device=device,
                                           user=device.user)
        #Set notification
        notification = kwargs['notification']
        gcm_notification.notification = notification
        
        #Set merchant
        merchant = kwargs['merchant']
        gcm_notification.merchant = merchant
        
        gcm_notification.save()

@receiver(new_customer)
def update_customer(sender, instance, **kwargs):
    #Add group
    group = Group.objects.get(name='customer')
    if group is not None:            
        instance.groups.add(group)
        instance.save()
  
    #Set Prefs
    prefs = UserPreferences()
    prefs.user = instance
    prefs.save()
         
