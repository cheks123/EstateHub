from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create Profile manually (or rely on signals if already added)
            Profile.objects.filter(user=user).update(
                phone_number=form.cleaned_data['phone_number'],
                user_type=form.cleaned_data['user_type']
            )

            login(request, user)
            return redirect('property_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
