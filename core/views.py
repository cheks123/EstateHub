from django.shortcuts import render
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

# Create your views here.


def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # You can configure this to send to your own email
        send_mail(
            subject=f"EstateHub Contact from {name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )

        messages.success(request, "Thank you for contacting us. We'll get back to you shortly.")
        
    return render(request, 'core/contact.html')

