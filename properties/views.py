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
