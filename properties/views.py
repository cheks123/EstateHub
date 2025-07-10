from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, PropertyImage
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .forms import PropertyForm, PropertyImageForm, CommentForm, PropertyImageFormSet
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib import messages
from .forms import MessageForm


# Create your views here.

def property_list(request):
    properties = Property.objects.filter(is_available=True)

    q = request.GET.get('q')
    max_price = request.GET.get('max_price')

    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(location__icontains=q)
        )

    if max_price:
        properties = properties.filter(price__lte=max_price)

    context = {
        'properties': properties,
        'query': q,
        'max_price': max_price
    }
    return render(request, 'properties/property_list.html', context)



from .models import Comment

def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    comments = property_obj.comments.select_related('user').order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.property = property_obj
            comment.user = request.user
            comment.save()
            return redirect('property_detail', pk=pk)
    else:
        comment_form = CommentForm()

    return render(request, 'properties/property_detail.html', {
        'property': property_obj,
        'comments': comments,
        'comment_form': comment_form
    })





@login_required
def upload_property(request):
    if Property.objects.filter(owner=request.user).count() >= 5:
        messages.error(request, "You have reached the limit of 5 listed properties.")
        return redirect('property_list')

    
    ImageFormSet = modelformset_factory(PropertyImage, form=PropertyImageForm, extra=3)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=PropertyImage.objects.none())
        
        if form.is_valid() and formset.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()

            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.save(commit=False)
                    image.property = property_obj
                    image.save()

            return redirect('property_list')
    else:
        form = PropertyForm()
        formset = ImageFormSet(queryset=PropertyImage.objects.none())

    return render(request, 'properties/upload_property.html', {
        'form': form,
        'formset': formset
    })




@require_POST
@login_required
def add_comment(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)

    # Don't allow more than one comment per user per property
    if property_obj.comments.filter(user=request.user).exists():
        return JsonResponse({'success': False, 'error': 'You have already commented on this property.'})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.property = property_obj
        comment.user = request.user
        comment.save()

        html = render_to_string('properties/includes/comment_single.html', {'comment': comment}, request=request)
        return JsonResponse({'success': True, 'comment_html': html})

    return JsonResponse({'success': False, 'error': 'Invalid comment data.'})



@require_POST
@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    new_content = request.POST.get('content')
    if new_content:
        comment.content = new_content
        comment.save()
        return JsonResponse({'success': True, 'updated_text': comment.content})
    return JsonResponse({'success': False})


@require_POST
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    comment.delete()
    return JsonResponse({'success': True})


@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if property.owner != request.user:
        messages.error(request, "You are not allowed to edit this property.")
        return redirect('property_detail', pk=pk)

    form = PropertyForm(request.POST or None, instance=property)
    formset = PropertyImageFormSet(
        request.POST or None,
        request.FILES or None,
        instance=property
    )
    
    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "Property updated successfully.")
        return redirect('property_detail', pk=property.pk)
    else:
        print("Form Errors:", form.errors)
        print("Formset Errors:", formset.errors)
        messages.error(request, "Please fix the errors below.")


    return render(request, 'properties/edit_property.html', {
        'form': form,
        'formset': formset
    })



@login_required
@require_POST
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if property.owner != request.user:
        messages.error(request, "You’re not allowed to delete this property.")
        return redirect('property_detail', pk=property.pk)

    property.delete()
    messages.success(request, "Property deleted successfully.")
    return redirect('property_list')




def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    comments = property.comments.all()

    # Messaging
    message_form = None
    if request.user.is_authenticated and request.user != property.owner:
        message_form = MessageForm()

        if request.method == 'POST' and 'send_message' in request.POST:
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.sender = request.user
                message.recipient = property.owner
                message.property = property
                message.save()
                messages.success(request, "Message sent to the property owner.")
                return redirect('property_detail', pk=pk)

    return render(request, 'properties/property_detail.html', {
        'property': property,
        'comments': comments,
        'message_form': message_form,
    })



#Grok implementation for deleting a property image

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, PropertyImage

@login_required
def delete_property_image(request, image_id):
    image = get_object_or_404(PropertyImage, id=image_id)
    property = image.property
    
    # Check if the user owns the property
    if property.owner != request.user:
        messages.error(request, "You are not authorized to delete this image.")
        return redirect('property_detail', property_id=property.id)
    
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('property_detail', property_id=property.id)


from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PropertyImageForm  # You'll create this form next

@login_required
def update_property_image(request, image_id):
    image = get_object_or_404(PropertyImage, id=image_id)
    property = image.property
    
    # Check if the user owns the property
    if property.owner != request.user:
        messages.error(request, "You are not authorized to update this image.")
        return redirect('property_detail', property_id=property.id)
    
    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, "Image updated successfully.")
            return redirect('property_detail', pk=property.id)
    else:
        form = PropertyImageForm(instance=image)
    
    return render(request, 'properties/update_property_image.html', {
        'form': form,
        'property': property,
        'image': image
    })

# properties/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, PropertyImage
from .forms import PropertyImageForm

@login_required
def add_property_image(request, pk):
    property = get_object_or_404(Property, id=pk)
    
    # Check if the user owns the property
    if property.owner != request.user:
        messages.error(request, "You are not authorized to add images to this property.")
        return redirect('property_detail', pk=property.id)
    
    # Check the number of existing images
    if property.images.count() >= 3:
        messages.error(request, "You cannot add more than 3 images to this property.")
        return redirect('property_detail', pk=property.id)
    
    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.property = property
            image.save()
            messages.success(request, "Image added successfully.")
            return redirect('property_detail', pk=property.id)
    else:
        form = PropertyImageForm()
    
    return render(request, 'properties/add_property_image.html', {
        'form': form,
        'property': property
    })