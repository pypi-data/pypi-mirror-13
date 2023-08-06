from rest_framework import permissions

class IsOwnerOrAdmin(permissions.IsAuthenticated):
    """
    Action-level permission
    """
    def has_permission(self, request, view):
        # only admin can list all users 
        return view.action == 'retrieve' or request.user.is_staff
    
    """
    Object-level permission.
    """
    def has_object_permission(self, request, view, obj):
        #check the admin user
        result = request.user and request.user.is_staff       
        #check the owner.
        result = result or (obj.user == request.user.username)
        return result
    
class CustomerAPIPermission(IsOwnerOrAdmin):
    """
    Action-level permission
    """
    def is_customer(self, user):        
        return user.groups.filter(name='customer').exists()
    
    def is_targeted_customer(self, view, user):
        try:
            return  view.get_object() == user
        except Exception:
            return True
    
    def has_permission(self, request, view):        
        result = view.action == 'create'        
        result = result or (self.is_customer(request.user) and self.is_targeted_customer(view, request.user))                 
        result = result or super(CustomerAPIPermission, self).has_permission(request, view)
        
        return result
    

class GCMAPIPermission(IsOwnerOrAdmin):
    """
    Action-level permission
    """
    def has_permission(self, request, view):        
        result = view.action == 'create'                    
        result = result or super(GCMAPIPermission, self).has_permission(request, view)
        
        return result
        

        