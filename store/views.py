from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder

def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)



def checkout(request):
    import json
    from django.conf import settings
    from http.client import HTTPSConnection
    from base64 import b64encode
    from .models import Transaction

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    total_amount = sum([item.product.price * item.quantity for item in items])

    midtrans_host = "api.sandbox.midtrans.com"
    midtrans_path = "/v2/charge"
    headers = {
        "Authorization": f"Basic {b64encode(settings.MIDTRANS_SERVER_KEY.encode()).decode()}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "payment_type": "bank_transfer",
        "transaction_details": {
            "order_id": f"ORDER-{order.id}",
            "gross_amount": total_amount,
        },
        "customer_details": {
            "first_name": request.user.first_name if request.user.is_authenticated else "Guest",
            "email": request.user.email if request.user.is_authenticated else "guest@example.com",
            "phone": "081234567890",
        }
    })

    print("Payload to Midtrans:", payload)  # Debug payload
    snap_token = None
    try:
        conn = HTTPSConnection(midtrans_host)
        conn.request("POST", midtrans_path, body=payload, headers=headers)
        response = conn.getresponse()
        payment_response = json.loads(response.read().decode())
        conn.close()

        print("Midtrans API Response:", payment_response)  # Debug API response

        if "token" in payment_response:
            snap_token = payment_response["token"]
        else:
            print("Midtrans Response Error:", payment_response)

        if snap_token:
            Transaction.objects.create(
                order=order,
                user=request.user,
                transaction_id=payment_response.get('transaction_id', 'N/A'),
                amount=total_amount,
                status=payment_response.get('transaction_status', 'Pending'),
                payment_response=payment_response,
            )
    except Exception as e:
        snap_token = None
        print(f"Error generating Snap Token: {e}")

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'snap_token': snap_token,
        'MIDTRANS_CLIENT_KEY': settings.MIDTRANS_CLIENT_KEY,
    }
    return render(request, 'store/checkout.html', context)
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Ensure all calculations are in IDR (Rupiah)
    total_amount = sum([item.product.price * item.quantity for item in items])

    # Generate Snap Token for Midtrans
    midtrans_host = "api.sandbox.midtrans.com"
    midtrans_path = "/v2/charge"
    midtrans_key = settings.MIDTRANS_SERVER_KEY
    headers = {
        "Authorization": f"Basic {b64encode(midtrans_key.encode()).decode()}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "payment_type": "bank_transfer",
        "transaction_details": {
            "order_id": f"{order.id}",
            "gross_amount": total_amount,
        },
        "customer_details": {
            "first_name": request.user.first_name if request.user.is_authenticated else "Guest",
            "last_name": "",
            "email": request.user.email if request.user.is_authenticated else "guest@example.com",
            "phone": "081234567890",  # Replace with actual phone logic if available
        }
    })

    snap_token = None
    try:
        # Log the payload for debugging
        print("Payload to Midtrans:", payload)

        # Send the request to Midtrans
        conn = HTTPSConnection(midtrans_host)
        conn.request("POST", midtrans_path, body=payload, headers=headers)
        response = conn.getresponse()
        payment_response = json.loads(response.read().decode())
        conn.close()

        # Log the API response for debugging
        print("Midtrans API Response:", payment_response)

        if "token" in payment_response:
            snap_token = payment_response["token"]
        else:
            print("Midtrans Response Error: No token in response", payment_response)  # Debugging

        # Save transaction to the database if token is generated
        if snap_token:
            Transaction.objects.create(
                order=order,
                user=request.user,
                transaction_id=payment_response.get('transaction_id', 'N/A'),
                amount=total_amount,
                status=payment_response.get('transaction_status', 'Pending'),
                payment_response=payment_response,
            )
    except Exception as e:
        snap_token = None
        print(f"Error generating Snap Token: {str(e)}")  # Debugging

    # Context to render checkout page
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'snap_token': snap_token,
        'MIDTRANS_CLIENT_KEY': settings.MIDTRANS_CLIENT_KEY,
    }
    return render(request, 'store/checkout.html', context)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.username}!')
            return redirect('store')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'store/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'Anda berhasil logout.')
    return redirect('login')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registrasi berhasil, silakan login.')
            return redirect('login')
    return render(request, 'store/register.html')

import requests
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        try:
            # Parsing request body
            body = json.loads(request.body)
            
            # Midtrans Snap API endpoint
            url = settings.MIDTRANS_BASE_URL

            # Headers with server key
            headers = {
                "Authorization": f"Basic {settings.MIDTRANS_SERVER_KEY.encode('ascii').decode('ascii')}",
                "Content-Type": "application/json"
            }

            # Payload for transaction (example)
            payload = {
                "transaction_details": {
                    "order_id": body.get("order_id", "order-id-123456"),
                    "gross_amount": body.get("gross_amount", 100000)
                },
                "customer_details": {
                    "first_name": body.get("first_name", "John"),
                    "last_name": body.get("last_name", "Doe"),
                    "email": body.get("email", "johndoe@example.com"),
                    "phone": body.get("phone", "08123456789")
                }
            }

            # Send request to Midtrans
            response = requests.post(url, json=payload, headers=headers)
            return JsonResponse(response.json(), safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)

import midtransclient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        try:
            # Parse request body
            body = json.loads(request.body)

            # Midtrans configuration
            snap = midtransclient.Snap(
                is_production=False,  # Set to True if using production mode
                server_key='Mid-server-hmm8a4bevYUybOzH5x-MvIDX',  # Replace with your Server Key
                client_key='Mid-client-UXuBITRfxBh8PUfC'  # Replace with your Client Key
            )

            # Payload for Snap transaction
            transaction_data = {
                "transaction_details": {
                    "order_id": body.get('order_id', 'order-id-12345'),  # Default order_id
                    "gross_amount": body.get('gross_amount', 100000)  # Default gross_amount
                },
                "customer_details": {
                    "first_name": body.get('first_name', 'John'),
                    "last_name": body.get('last_name', 'Doe'),
                    "email": body.get('email', 'johndoe@example.com'),
                    "phone": body.get('phone', '08123456789')
                }
            }

            # Create Snap transaction and get token
            snap_response = snap.create_transaction(transaction_data)

            # Return token to frontend
            return JsonResponse({"token": snap_response['token']})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)

import midtransclient
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        try:
            # Parse request body
            body = json.loads(request.body)

            # Midtrans configuration
            snap = midtransclient.Snap(
                is_production=settings.MIDTRANS_IS_PRODUCTION,  # Set True for production
                server_key=settings.MIDTRANS_SERVER_KEY,
                client_key=settings.MIDTRANS_CLIENT_KEY,
            )

            # Transaction details
            transaction_data = {
                "transaction_details": {
                    "order_id": body.get('order_id', 'order-id-12345'),
                    "gross_amount": body.get('gross_amount', 100000),
                },
                "customer_details": {
                    "first_name": body.get('first_name', 'John'),
                    "last_name": body.get('last_name', 'Doe'),
                    "email": body.get('email', 'johndoe@example.com'),
                    "phone": body.get('phone', '08123456789'),
                },
            }

            # Create Snap Token
            snap_response = snap.create_transaction(transaction_data)

            # Return Snap Token
            return JsonResponse({"token": snap_response['token']})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

import midtransclient
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        try:
            # Parse request body
            body = json.loads(request.body)

            # Midtrans configuration
            snap = midtransclient.Snap(
                is_production=settings.MIDTRANS_IS_PRODUCTION,
                server_key=settings.MIDTRANS_SERVER_KEY,
                client_key=settings.MIDTRANS_CLIENT_KEY,
            )

            # Transaction details
            transaction_data = {
                "transaction_details": {
                    "order_id": body.get('order_id', 'order-id-12345'),
                    "gross_amount": body.get('gross_amount', 100000),
                },
                "customer_details": {
                    "first_name": body.get('first_name', 'John'),
                    "last_name": body.get('last_name', 'Doe'),
                    "email": body.get('email', 'johndoe@example.com'),
                    "phone": body.get('phone', '08123456789'),
                },
            }

            # Create Snap Token
            snap_response = snap.create_transaction(transaction_data)

            # Return Snap Token
            return JsonResponse({"token": snap_response['token']})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

import midtransclient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        try:
            # Parse request body
            body = json.loads(request.body)

            # Midtrans Snap Client Configuration
            snap = midtransclient.Snap(
                is_production=settings.MIDTRANS_IS_PRODUCTION,
                server_key=settings.MIDTRANS_SERVER_KEY,
                client_key=settings.MIDTRANS_CLIENT_KEY,
            )

            # Transaction Details
            transaction_data = {
                "transaction_details": {
                    "order_id": body.get('order_id', 'order-id-12345'),
                    "gross_amount": body.get('gross_amount', 100000),
                },
                "customer_details": {
                    "first_name": body.get('first_name', 'John'),
                    "last_name": body.get('last_name', 'Doe'),
                    "email": body.get('email', 'johndoe@example.com'),
                    "phone": body.get('phone', '08123456789'),
                },
            }

            # Create Snap Transaction
            snap_response = snap.create_transaction(transaction_data)

            # Return Snap Token
            return JsonResponse({"token": snap_response['token']})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
