from datetime import date
from mezzanine import template
from happystamp.models import Transaction

register = template.Library()

@register.inclusion_tag("includes/daily_metrics.html",
                        takes_context=True)
def daily_metrics(context):
    """
    Renders the daily metrics for the admin dashboard widget.
    """
    
    query_set = Transaction.objects.filter(created__gt=date.today(),
                                           card__program__user=context.get('request', None).user);
                                                                                     
    reward_count = query_set.filter(debit__gt=0).count();            
    redeem_count = query_set.filter(credit__gt=0).count()
    
    context.update({'reward_count': reward_count,
                    'redeem_count': redeem_count    
                    })
    return context