from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from properties.models import Property  
from .forms import UserUpdateForm
from django.contrib import messages



# Create your views here.


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




@login_required
def user_profile(request):
    user = request.user
    user_properties = Property.objects.filter(owner=user)

    return render(request, 'accounts/profile.html', {
        'user_info': user,
        'properties': user_properties,
    })




# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         form = UserUpdateForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Profile updated successfully.")
#             return redirect('user_profile')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = UserUpdateForm(instance=request.user)

#     return render(request, 'accounts/edit_profile.html', {'form': form})


# from .forms import UserUpdateForm, ProfileForm

@login_required
def edit_profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)

    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('user_profile')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/edit_profile.html', {
        'form': user_form,
        'profile_form': profile_form
    })
