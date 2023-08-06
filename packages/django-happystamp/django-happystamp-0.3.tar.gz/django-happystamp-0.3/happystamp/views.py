from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.authentication import BasicAuthentication

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from happystamp.models import Merchant
from happystamp.models import Program
from happystamp.models import ProgramStep
from happystamp.models import Card 
from happystamp.models import Transaction
from happystamp.models import UserPreferences
from happystamp.models import GCMNotification
from happystamp.models import GCMDevice
from happystamp.models import new_customer

from happystamp.serializers import MerchantSerializer
from happystamp.serializers import UserSerializer
from happystamp.serializers import ProgramSerializer
from happystamp.serializers import ProgramStepSerializer
from happystamp.serializers import CardSerializer
from happystamp.serializers import TransactionSerializer
from happystamp.serializers import UserPreferencesSerializer
from happystamp.serializers import GCMSerializer

from rest_framework.permissions import AllowAny

from happystamp.permissions import IsOwnerOrAdmin
from happystamp.permissions import CustomerAPIPermission
from happystamp.permissions import GCMAPIPermission

from django.shortcuts import get_object_or_404



def add_group(user, group_name):
    group = Group.objects.get(name=group_name)
    if group is not None:
        user.groups.add(group)
    return user

###############################################################################
#                              Merchant                                       #
###############################################################################  
class MerchantAPI(viewsets.ModelViewSet):
    """
    Merchant API endpoint
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = (IsOwnerOrAdmin,)
    authentication_classes = (BasicAuthentication,)
    
    @detail_route(methods=['get'])
    def programs(self, request, pk=None):
        queryset = Program.objects.filter(merchant__pk=pk)
        serializer = ProgramSerializer(queryset,
                                       context={'request':request},
                                       many=True)
        return Response(serializer.data)
    
###############################################################################
#                                Program Step                                 #
############################################################################### 
class ProgramStepAPI(viewsets.ModelViewSet):
    """
    ProgramStep API endpoint
    """
    queryset = ProgramStep.objects.all()
    serializer_class = ProgramStepSerializer  
    permission_classes = (IsOwnerOrAdmin,)
    
###############################################################################
#                                Program                                      #
############################################################################### 
class ProgramAPI(viewsets.ModelViewSet):
    """
    Program API endpoint
    """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer 
    permission_classes = (IsOwnerOrAdmin,)  

    
###############################################################################
#                               Customer                                      #
###############################################################################  
class CustomerAPI(viewsets.ModelViewSet):
    """
    Customer API endpoint
    """     
    queryset = User.objects.all()
    serializer_class = UserSerializer 
    permission_classes = (CustomerAPIPermission,)
    
    def perform_create(self, serializer):
        instance = serializer.save()
        new_customer.send(sender=self.__class__, 
                          instance=instance) 
            
            
    @list_route(methods=['get'])
    def account(self, request, **kwargs):        
        serializer = UserSerializer(self.request.user,
                                    context={'request':request})
                
        return Response(serializer.data)
        
    @detail_route(methods=['get'])
    def cards(self, request, **kwargs):
        queryset = Card.objects.filter(owner__pk=request.user.id,
                                       end_date__isnull=True)
        serializer = CardSerializer(queryset,
                                    context={'request':request},
                                    many=True)
        return Response(serializer.data)
    
    @detail_route(methods=['post'])
    def enroll(self, request, **kwargs):
        program = get_object_or_404(Program, enroll_key=request.data['enroll_key'])
        
        if program.can_enroll():
            card = program.enroll(request.user)            
            serializer = CardSerializer(card,
                                        context={'request':request})
            
            return Response(serializer.data)
        else:
            return Response(status=HTTP_401_UNAUTHORIZED)
    
    @detail_route(methods=['post'])
    def redeem(self, request, **kwargs):
        program = get_object_or_404(Program, redeem_key=request.data['redeem_key'])
        card = get_object_or_404(Card, program__id=program.id, owner__pk = request.user.id)
        if card.can_redeem():
            serializer = TransactionSerializer(card.redeem(),
                                               context={'request':request})
            
            return Response(serializer.data)
        else:
            return Response(status=HTTP_401_UNAUTHORIZED)
        
    @detail_route(methods=['post'])
    def reward(self, request, **kwargs):        
        program      = get_object_or_404(Program, reward_key=request.data['reward_key'])
        program_step = get_object_or_404(ProgramStep, program__id=program.id, reward_passcode=request.data['step'])
        card         = get_object_or_404(Card, program__id=program.id, owner__pk = request.user.id)
                
        if program_step is not None and card.can_reward(program_step):
            serializer = TransactionSerializer(card.reward(program_step),
                                               context={'request':request})        
            return Response(serializer.data)
        else:
            return Response(status=HTTP_401_UNAUTHORIZED)
        
    @detail_route(methods=['get', 'put'])
    def preferences(self, request, **kwargs):
        if  request.method == 'GET':
            user_preferences = get_object_or_404(UserPreferences, user__pk=request.user.id)
            serializer = UserPreferencesSerializer(user_preferences,
                                                   context={'request':request})
            return Response(serializer.data)
        else:
            user_preferences = get_object_or_404(UserPreferences, user__pk=request.user.id)            
            serializer = UserPreferencesSerializer(user_preferences, 
                                                   data = request.data,
                                                   context={'request':request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        
            user_preferences  = serializer.save(force_update=True)
            return Response(serializer.data)

    @list_route(methods=['get'])
    @renderer_classes((TemplateHTMLRenderer,))
    def notifications(self, request, **kwargs):            
        notifications =  GCMNotification.objects.filter(user__pk=request.user.id).all()
        return Response({'notifications': notifications}, template_name='customer/notifications.html')

###############################################################################
#                                  Card                                       #
############################################################################### 
class CardAPI(viewsets.ModelViewSet):
    """
    Card API endpoint
    """
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = (IsOwnerOrAdmin,)    
    
    
    @detail_route(methods=['get'])
    def transactions(self, request, pk=None):
        queryset = Transaction.objects.filter(card__pk=pk)
        serializer = TransactionSerializer(queryset,
                                           context={'request':request},
                                           many=True)

        return Response(serializer.data)

###############################################################################
#                              Transaction                                    #
############################################################################### 
class TransactionAPI(viewsets.ModelViewSet):
    """
    Transaction API endpoint    
    """
    queryset = Transaction.objects.all()       
    serializer_class = TransactionSerializer
    permission_classes = (IsOwnerOrAdmin,)
    
###############################################################################
#                              Reset Password                                 #
############################################################################### 
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):    
    form = PasswordResetForm(request.data)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'token_generator': default_token_generator,           
            'email_template_name': 'password_reset_email.html',
            'subject_template_name': 'registration/password_reset_subject.txt',
            'request': request            
        }
        
        form.save(**opts)
        return Response(status=HTTP_201_CREATED)
    
    return Response(status=HTTP_400_BAD_REQUEST)

    
###############################################################################
#                                User Preferences                             #
###############################################################################    
class UserPreferencesAPI(viewsets.ModelViewSet):
    """
    UserPreferences API endpoint
    """
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer  
    permission_classes = (IsOwnerOrAdmin,)   

###############################################################################
#                              GCCM Device                                    #
############################################################################### 
class GCMAPI(viewsets.ModelViewSet):
    """
    GCM API endpoint
    """
    queryset = GCMDevice.objects.all()
    serializer_class = GCMSerializer
    permission_classes = (GCMAPIPermission,) 
     
    
      
    