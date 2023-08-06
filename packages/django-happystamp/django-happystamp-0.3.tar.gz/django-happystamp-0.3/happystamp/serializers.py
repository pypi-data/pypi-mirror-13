from rest_framework import serializers
from happystamp.models import Merchant 
from happystamp.models import ProgramStep
from happystamp.models import Program
from happystamp.models import Card
from happystamp.models import Transaction
from happystamp.models import UserPreferences
from happystamp.models import GCMDevice

from html2text import html2text

from django.contrib.auth.models import User
from rest_framework.fields import FileField


###############################################################################
#                                 User                                        #
###############################################################################  
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'email', 'username', 'first_name', 'last_name', 'password')        
        write_only_fields = ('password', )      

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        
        return user
    
    
    
###############################################################################
#                              User Preferences                               #
###############################################################################  
class UserPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ('url', 'notif_email', 'notif_push')              

###############################################################################
#                              Merchant                                       #
###############################################################################  
class MerchantSerializer(serializers.HyperlinkedModelSerializer):
    brand_logo = FileField(use_url=True)
    class Meta:
        model = Merchant
        fields = ('url', 'name', 'email', 'address', 'phone', 'content', 'brand_logo')   

###############################################################################
#                              ProgramStep                                     #
############################################################################### 
class ProgramStepSerializer(serializers.HyperlinkedModelSerializer):
    reward_logo = FileField(use_url=True)
          
    class Meta:
        model = ProgramStep
        fields = ('url', 'id', 'redeem', 'reward', 'reward_logo')        
        
###############################################################################
#                              Program                                     #
############################################################################### 
class ProgramSerializer(serializers.HyperlinkedModelSerializer): 
    steps = ProgramStepSerializer(many=True, read_only=True)
    merchant = MerchantSerializer(read_only=True)
    program_logo = FileField(use_url=True)
    
    class Meta:
        model = Program
        fields = ('url', 'id', 'enroll_key', 'redeem_key', 'reward_key', 'publish_date', 
                  'expiry_date', 'content', 'program_logo', 'steps', 'merchant')
        read_only_fields = ('enroll_key', 'redeem_key', 'reward_key', 'id', )
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['content'] = html2text(ret['content'])[:-2]
        return ret      

###############################################################################
#                              Transaction                                    #
###############################################################################  
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ('url', 'credit', 'debit', 'detail', 'created')

###############################################################################
#                                 Card                                        #
############################################################################### 
class CardSerializer(serializers.HyperlinkedModelSerializer):
    program = ProgramSerializer(read_only=True)
    active_transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Card
        fields = ('url', 'id', 'effective_date', 'end_date', 'cycle_start_date', 'credit', 
                  'program', 'active_transactions') 
        read_only_fields = ('credit', 'id', )

###############################################################################
#                                   GCM                                       #
###############################################################################  
class GCMSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GCMDevice
        fields = ('url', 'id', 'dev_id', 'reg_id', 'is_active', 'user')
        read_only_fields = ('is_active', 'id', )   

                