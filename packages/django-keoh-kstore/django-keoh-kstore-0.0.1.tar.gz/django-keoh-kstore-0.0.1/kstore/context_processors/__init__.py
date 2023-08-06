
from kstore.models import BasicConfiguration, MailMessage, MailContact

def basic_configuration_context_processor(request):
    try:
        config = BasicConfiguration.objects.get(id=1)
    except Exception as e:
        config = {
            'company_name': 'No company Name'
        }

    return {'superconfig': config}

def num_unread_messages(request):
    num = MailMessage.objects.new_messages(request.user).count()
    return {'num_unread_messages': num}

def return_contacts(request):
    contacts = MailContact.objects.filter(owner=request.user)
    return {'mail_contacts': contacts, 'num_mail_contacts': contacts.count()}
