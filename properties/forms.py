from django import forms
from .models import Property, PropertyImage, Comment, Message
from django.forms import inlineformset_factory
from django.forms import  BaseInlineFormSet



class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image']

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'property_type','description', 'location', 'price']



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }

PropertyImageFormSet = inlineformset_factory(
    Property,
    PropertyImage,
    fields=('image',),
    extra=1,
    can_delete=True
)






class BasePropertyImageFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BasePropertyImageFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True  # ✅ Allow empty image inputs

PropertyImageFormSet = inlineformset_factory(
    Property,
    PropertyImage,
    fields=('image',),
    extra=1,
    can_delete=True,
    formset=BasePropertyImageFormSet  # ✅ use the custom base
)







class MessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Write your message here...',
        'rows': 3
    }))

    class Meta:
        model = Message
        fields = ['content']




