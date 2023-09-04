from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SignUpForm
from .models import UserProfile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.shortcuts import render, redirect
from .models import UploadedFile
from .forms import UploadFileForm
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import requests
from django.conf import settings

class UserLoginView(LoginView):
    template_name = 'login.html'

def send_mailgun_email(to_email, subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/Filsharing/messages",
        auth=("api", "pubkey-94d61b110a1f1d371c0ab404a9ed3837"),
        data={
            "from": "Excited User <mailgun@Filesharing>",
            "to": [to_email],
            "subject": subject,
            "text": text
        }
    )

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            UserProfile.objects.create(user=user, user_type=form.cleaned_data['user_type'])
            login(request, user)

            if settings.EMAIL_ENABLED:
                mail_subject = 'Activate your account'
                activation_link = "{}/activate/{}-{}/".format(
                    settings.SITE_URL,
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    default_token_generator.make_token(user)
                )
                text = "Click the following link to activate: {}".format(activation_link)
                to_email = form.cleaned_data.get('email')
                
                send_mailgun_email(to_email, mail_subject, text)

            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user_profile = UserProfile.objects.get(user=user)
        user_profile.email_verified = True
        user_profile.save()
        login(request, user)
        return redirect('upload')  
    else:
        return render(request, 'activation_invalid.html') 

from django.contrib.auth.decorators import login_required

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['file'].name
            if filename.endswith(('.pptx', '.docx', '.xlsx')):
                uploaded_file_instance = form.save(commit=False)  
                uploaded_file_instance.uploaded_by = request.user  
                uploaded_file_instance.save()  
                return redirect('file_list')
            else:
                form.add_error('file', 'Unsupported file type')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def file_list(request):
    files = UploadedFile.objects.all()
    return render(request, 'file_list.html', {'files': files})

def download_file(request, encrypted_id):
    try:
        file_id = uuid.UUID(encrypted_id)
        uploaded_file = UploadedFile.objects.get(id=file_id)
        if uploaded_file.is_accessible_by(request.user):
            response = HttpResponse(uploaded_file.file.read())
            response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name}"'
            return response
        else:
            return HttpResponse("Access denied", status=403)
    except (ValueError, UploadedFile.DoesNotExist):
        return HttpResponse("File not found", status=404)
