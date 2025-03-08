
def user_roles(request):
    """
    Add user roles to context for all templates
    """
    context = {
        'user_roles': [],
        'is_admin': False,
        'is_seller': False,
        'is_buyer': False,
        'is_inspector': False,
        'is_legal': False,
    }
    
    if request.user.is_authenticated:
        roles = request.user.roles.all()
        role_names = [role.name for role in roles]
        
        context['user_roles'] = role_names
        context['is_admin'] = 'admin' in role_names
        context['is_seller'] = 'seller' in role_names
        context['is_buyer'] = 'buyer' in role_names
        context['is_inspector'] = 'inspector' in role_names
        context['is_legal'] = 'legal' in role_names
    
    return context