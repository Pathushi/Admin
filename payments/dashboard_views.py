import io
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# PDF Generation imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Import models from your payments app
from .models import Payment, FailedPayment, ContactMessage

User = get_user_model()

@login_required
def dashboard_stats(request):
    """Main Dashboard Stats for Summary Cards and Analytics"""
    today = timezone.now().date()
    
    # Financial Stats based on the Payment model
    total_collections = Payment.objects.filter(status="Success").aggregate(Sum('amount'))['amount__sum'] or 0
    month_donations = Payment.objects.filter(
        status="Success", 
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # New counters for Dashboard Cards
    failed_count = FailedPayment.objects.count()
    message_count = ContactMessage.objects.count()

    # Pie Chart Data (Categories based on 'donate_to' field)
    category_data = list(Payment.objects.filter(status="Success").values('donate_to').annotate(
        value=Sum('amount')
    ))

    # Recent Activity (Latest 10 successful donations)
    recent_activity = list(Payment.objects.filter(status="Success").order_by('-created_at')[:10].values(
        'created_at', 'first_name', 'donate_to', 'amount', 'transaction_id'
    ))

    return JsonResponse({
        "summary": {
            "total": float(total_collections),
            "month": float(month_donations),
            "failed_total": failed_count,
            "new_messages": message_count
        },
        "pie_chart": category_data,
        "recent": recent_activity
    })

@login_required
def donations_list(request):
    """Full donations table with search and filtering"""
    queryset = Payment.objects.all().order_by('-created_at')

    # Filtering Logic based on GET parameters
    name = request.GET.get('name')
    country = request.GET.get('country')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if name:
        queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
    if country:
        queryset = queryset.filter(country__icontains=country)
    if category:
        queryset = queryset.filter(donate_to=category)
    if start_date and end_date:
        queryset = queryset.filter(created_at__date__range=[start_date, end_date])

    donations = list(queryset.values(
        'transaction_id', 'first_name', 'last_name', 'email', 'phone',
        'amount', 'country', 'donate_to', 'status', 'created_at'
    ))
    return JsonResponse({"donations": donations})

@login_required
def failed_donations_list(request):
    """Display items from the FailedPayment model"""
    failed = list(FailedPayment.objects.all().order_by('-created_at').values(
        'transaction_id', 'first_name', 'email', 'amount', 'donate_to', 'created_at'
    ))
    return JsonResponse({"failed_payments": failed})

@login_required
def contact_messages_list(request):
    """Display items from the ContactMessage model"""
    messages = list(ContactMessage.objects.all().order_by('-created_at').values(
        'name', 'email', 'phone', 'message', 'created_at'
    ))
    return JsonResponse({"messages": messages})

@login_required
def export_donations_pdf(request):
    """Generate professional PDF report"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header Design
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "CEYLON BAITHULMAL FUND - DONATION REPORT")
    p.setFont("Helvetica", 10)
    p.drawString(100, 735, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    p.line(100, 730, 550, 730)

    donations = Payment.objects.filter(status="Success").order_by('-created_at')
    
    y = 700
    p.setFont("Helvetica-Bold", 9)
    p.drawString(100, y, "Date")
    p.drawString(180, y, "Donor Name")
    p.drawString(350, y, "Category")
    p.drawString(480, y, "Amount")
    
    p.setFont("Helvetica", 8)
    for d in donations:
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
        p.drawString(100, y, d.created_at.strftime('%Y-%m-%d'))
        p.drawString(180, y, f"{d.first_name} {d.last_name}")
        p.drawString(350, y, d.donate_to)
        p.drawString(480, y, f"{d.amount:.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='Baithulmal_Donation_Report.pdf')

@login_required
def manage_users(request):
    """List all admin users from Custom User Model"""
    users = list(User.objects.values('id', 'username', 'role', 'status'))
    return JsonResponse({"users": users})

@login_required
def delete_user(request, user_id):
    """Security-focused user deletion"""
    if request.method == "POST":
        user_to_delete = get_object_or_404(User, id=user_id)
        # Prevent self-deletion
        if user_to_delete.id != request.user.id:
            user_to_delete.delete()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)