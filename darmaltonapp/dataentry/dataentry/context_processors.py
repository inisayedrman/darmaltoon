from django.contrib.admin.models import LogEntry

def recent_actions(request):
    recent_actions = LogEntry.objects.select_related('content_type', 'user').order_by('-action_time')[:10]
    return {'recent_actions': recent_actions}

def user_role(request):
    if request.user.is_authenticated:
        return {'user_role': request.user.user_type}
    return {}

def user_role(request):
    if request.user.is_authenticated:
        return {'user_role': request.user.profile.user_type}
    return {}

def new_action_count(request):
    if request.user.is_authenticated:
        # Determine the count of new action records for the logged-in user
        seen_action_ids = request.session.get('seen_action_ids', [])
        new_action_count = LogEntry.objects.filter(user=request.user).exclude(id__in=seen_action_ids).count()
    else:
        new_action_count = 0
    
    # Return the new_action_count as a dictionary
    return {'new_action_count': new_action_count}