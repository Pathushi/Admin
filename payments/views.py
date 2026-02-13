import uuid
import logging
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from .models import Payment, ContactMessage
from payments.gateway import WebXPayProvider

logger = logging.getLogger(__name__)

LKR_PER_USD = Decimal("308.45")

@csrf_exempt
def create_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        user_currency = request.POST.get("currency_preference", "USD").upper()
        amount_str = request.POST.get("amount", "").strip()
        if amount_str.lower() == "other":
            amount_str = request.POST.get("other_amount", "").strip()

        raw_amount = Decimal(amount_str)

        if user_currency == "USD":
            final_lkr_amount = (raw_amount * LKR_PER_USD).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            final_lkr_amount = raw_amount

        # CLEANED: Saving plaintext data now
        payment = Payment.objects.create(
            first_name=request.POST.get("first_name", "Donor"),
            last_name=request.POST.get("last_name", "User"),
            email=request.POST.get("email", "").strip(),
            phone="".join(filter(str.isdigit, request.POST.get("phone", ""))),
            country=request.POST.get("country", "Sri Lanka"),
            donation_option=request.POST.get("donation_option", ""),
            donate_to=request.POST.get("donate_to", "General"),
            amount=final_lkr_amount,
            status="Pending",
        )

        gateway = WebXPayProvider()
        formatted_lkr = f"{final_lkr_amount:.2f}"
        payment_data = gateway.get_payment_params(payment, formatted_lkr)

        return JsonResponse(payment_data)

    except Exception as e:
        logger.exception("Create payment error")
        return JsonResponse({"error": str(e)}, status=500)


def send_thank_you_email(payment, display_amount):
    """Sends a formatted thank you email to the donor matching the requested UI."""
    now = timezone.now()
    # Formatting date/time to match the screenshot (DD/MM/YYYY | HH:MM)
    date_display = now.strftime('%d/%m/%Y | %H:%M')
    timestamp = now.strftime('%Y%m%d%H%M')

    full_name = f"{payment.first_name} {payment.last_name}".strip()
    ref_no = f"CBF-{payment.first_name.replace(' ', '')}{payment.last_name.replace(' ', '')}-{timestamp}"

    subject = f"CEYLON BAITHULMAL FUND | YOUR DONATION | {now.strftime('%d/%m/%Y')} | {now.strftime('%H:%M')}"
    from_email = settings.EMAIL_HOST_USER
    to_email = [payment.email]
    
    # Use LKR as the base currency for display
    amount_display = f"LKR {display_amount:.2f}"

    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 650px; margin: auto; padding: 20px;">
          <h2 style="color: #2c5e77; font-size: 24px; text-transform: uppercase; border-bottom: 2px solid #92BC13; padding-bottom: 10px;">
            CEYLON BAITHULMAL FUND
          </h2>
          
          <p>Dear Sir/Madam <strong>{full_name}</strong>,</p>
          <p>Thank you for your valuable donation. Your support helps us serve better and reach more people.</p>
          
          <div style="background: #f9f9f9; padding: 25px; border-radius: 8px; border-left: 5px solid #92BC13; margin: 20px 0;">
            <h3 style="color: #92BC13; margin-top: 0; text-transform: uppercase; font-size: 18px;">YOUR DONATION DETAILS</h3>
            
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 8px 0; font-weight: bold; width: 150px;">Ref No:</td>
                <td style="padding: 8px 0;">{ref_no}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Name:</td>
                <td style="padding: 8px 0;">{full_name}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Donation Type:</td>
                <td style="padding: 8px 0;">{payment.donation_option}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Appeal:</td>
                <td style="padding: 8px 0;">{payment.donate_to}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Country:</td>
                <td style="padding: 8px 0;">{payment.country}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Date | Time:</td>
                <td style="padding: 8px 0;">{date_display}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; font-weight: bold;">Amount:</td>
                <td style="padding: 8px 0; color: #92BC13; font-weight: bold; font-size: 1.1em;">{amount_display}</td>
              </tr>
            </table>
          </div>
          
          <p style="font-style: italic;">May Allah reward you and your family.</p>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0 10px 0;">
          
          <div style="font-size: 13px; color: #666;">
            <p><strong>Ceylon Baithulmal Fund</strong><br>
            <a href="https://baithulmal.lk" style="color: #2c5e77; text-decoration: none;">baithulmal.lk</a> | 
            <a href="mailto:c.baithulmal@gmail.com" style="color: #2c5e77; text-decoration: none;">c.baithulmal@gmail.com</a><br>
            (+94) 11 25 99 075</p>
          </div>
        </div>
      </body>
    </html>
    """

    email = EmailMultiAlternatives(subject, "", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

@csrf_exempt
def payment_callback(request):
    data = request.POST if request.POST else request.GET
    raw_id = data.get("order_id") or data.get("callback_id")
    transaction_id = raw_id.strip() if raw_id else None
    status_code = data.get("status_code")

    try:
        # 1. Direct Lookup
        payment = Payment.objects.get(transaction_id__iexact=transaction_id)

        if status_code == "00":
            payment.status = "Success"
            payment.save()

            # 2. Direct Email Attempt
            try:
                send_thank_you_email(payment, payment.amount)
            except Exception as e:
                logger.error(f"Email failure: {e}")

            # 3. Direct Success Card Rendering
            return HttpResponse(f"""
    <html>
    <head>
        <title>Success | BaithulMal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
                background-color: #f0f2f5; 
            }}
            .card {{ 
                background: white; 
                padding: 50px 40px; 
                border-radius: 16px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.08); 
                max-width: 480px; 
                width: 90%; 
                text-align: center;
                border-top: 6px solid #92BC13;
            }}
            .icon-circle {{
                width: 80px;
                height: 80px;
                background: #f1f8e9;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto 25px;
            }}
            .icon-check {{
                color: #92BC13;
                font-size: 40px;
                font-weight: bold;
            }}
            h1 {{ 
                color: #2c5e77; 
                margin: 0 0 15px 0; 
                font-size: 28px;
                font-weight: 700;
            }}
            p {{ 
                color: #555; 
                font-size: 17px; 
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .amount-box {{
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                color: #92BC13;
                font-size: 22px;
                margin-bottom: 30px;
                border: 1px solid #eee;
            }}
            .btn {{ 
                background: #92BC13; 
                color: white; 
                padding: 14px 32px; 
                text-decoration: none; 
                border-radius: 8px; 
                font-weight: bold; 
                display: inline-block; 
                transition: background 0.3s ease;
                font-size: 16px;
            }}
            .btn:hover {{
                background: #7da110;
            }}
            .footer-text {{
                margin-top: 25px;
                font-size: 14px;
                color: #888;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon-circle">
                <span class="icon-check">✓</span>
            </div>
            <h1>Alhamdulillah!</h1>
            <p>Thank you, <strong>{payment.first_name}</strong>. Your generous contribution has been received.</p>
            
            <div class="amount-box">
                LKR {payment.amount:.2f}
            </div>

            <a href="https://baithulmal.lk/" class="btn">Return to Home Page</a>
            
            <div class="footer-text">
                May Allah reward you and your family.
            </div>
        </div>
    </body>
    </html>
""")
        else:
            payment.status = "Failed"
            payment.save()
            return HttpResponse(f"Payment failed. Status: {status_code}")

    except Payment.DoesNotExist:
        return HttpResponse("Transaction not found.", status=404)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        return HttpResponse("A system error occurred.", status=500)

@csrf_exempt
def contact_us_view(request):
    # (Remains unchanged as it was already plaintext)
    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()
            message = request.POST.get("message", "").strip()
            ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
