from django.shortcuts import render,redirect
from petapp.models import Pet,Cart,Profile, Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Q
import razorpay
# from django.core.mail import EmailMessage
from django.core.mail import send_mail

categories = Pet.objects.values('type').distinct()

# Create your views here.
def home(request):
    #print ('after login in home:',request.user.is_authenticated)
    context={}
    data= Pet.objects.all()
    context['pets'] = data
    # print(catogories)
    context['types'] = categories
    return render(request,'index.html',context)

def register(request):
    context = {}
    context['types'] = categories
    if request.method=='GET':
        return render(request,'register.html',context)
    else:
        u=request.POST['username']
        e=request.POST['email']
        p=request.POST['password']
        cp=request.POST['confirmpassword']
        if u=='' or e=='' or p=='' or cp=='':
            context['error']='Please fill all details'
            return render(request,'register.html',context)
        elif p != cp:
            context['error']='Password and confirm password must be same'
            return render(request,'register.html',context)
        elif User.objects.filter(username=u).exists():
            context['error']='Username already exists!!'
            return render(request,'register.html',context) 
        else:
            user=User.objects.create(username=u,email=e)
            user.set_password(p) #password encryption
            user.save()
            context['success']='Registered Successfully!!Please Login'
            return render(request,'login.html',context)

def userlogin(request):
    context={}
    context['types'] = categories
    if request.method=='GET':
        return render(request,'login.html',context)
    else:
        # context={}
        #user login code
        u=request.POST['username']
        p=request.POST['password']
        user = authenticate(username=u, password=p)
        if user is None:
            #wrong details
            # print('Wrong credentials')
            context['error']='Invalid Username of Password'
            return render(request,'login.html',context)
        else:
            # print('succesful authentication')
            # print(request.user)
            login(request,user)
            messages.success(request,'Logged in successfully !!') # messagemiddlware (method successhas been called)
            return redirect('/')
        
def userLogout(request):
    logout(request) #inbuilt logout funtion
    messages.success(request,'Logged out successfully !!') # messagemiddlware (method successhas been called)
    return redirect('/')

def aboutus(request):
    context = {}
    context['types'] = categories
    return render(request,'aboutus.html',context)

def contactus(request):
    context = {}
    context['types'] = categories
    return render(request,'contactus.html', context)

def petDetails(request,petid):
    data=Pet.objects.get(id=petid)
    context={}
    context['pet'] = data
    context['types'] = categories
    return render(request,'details.html',context)

def searchByCategory(request,searchBy):
    data = Pet.objects.filter(type =  searchBy)
    #select * from pet where type = searchBy;
    context = {}
    context['pets'] = data
    context['types'] = categories
    return render(request,'index.html',context)

def searchByRange(request):
    #select * from Pet where price >=15000 and price <= 20000
    minprice = request.GET['min']
    maxprice = request.GET['max']
    c1 = Q(price__gte = minprice)
    c2 = Q(price__lte = maxprice) #constructor called
    #print (minprice,maxprice)
    data = Pet.objects.filter(c1 & c2)
    context = {}
    context['pets'] = data
    return render(request,'index.html',context)

def sortPetsByPrice(request,dir):
    #data = Pet.objects.all().order_by('price')
    if dir == 'asc':
        col="price"
    else:
        col="-price"
    data = Pet.objects.all().order_by(col)
    context = {}
    context['pets'] = data
    return render(request,'index.html',context)

# def addToCart(request,petid):
#     user = request.user
#     pet = Pet.objects.get(id = petid)
#     cart = Cart.objects.create(pid = pet, uid = user)
#     cart.save()
#     messages.success(request,'Pet added to cart successfully !!')
#     return redirect('/')

def addToCart(request,petid):
    userid = request.user.id
    if userid:
        pet = Pet.objects.get(id = petid)
        cart = Cart.objects.create(pid = pet, uid = request.user)
        cart.save()
        messages.success(request,'Pet added to cart successfully !!')
        return redirect('/')
    else:
        messages.error(request,'Please login')
        return redirect('/login')

def showMyCart(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context = {}
    context['cartlist'] = data
    count = len(data)
    total = 0
    for cart in data:
        total += cart.pid.price*cart.quantity
    context ['count'] = count
    context ['total'] = total
    return render(request,'cart.html',context)

def removeCart(request,cartid):
    cart = Cart.objects.filter(id = cartid)
    cart.delete()
    messages.success(request,'Pet added to cart successfully !!')
    return redirect('/mycart')


def updateQuantity(request,cartid,oprn):
    if oprn == 'incr':
        cart = Cart.objects.filter(id = cartid)
        qty = cart[0].quantity
        cart.update(quantity = qty+1)
        return redirect('/mycart')
    else:
        cart = Cart.objects.filter(id = cartid)
        qty = cart[0].quantity
        cart.update(quantity = qty-1)
        return redirect('/mycart')
    
def confirmOrder(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context = {}
    context ['types'] = categories
    context['cartlist'] = data
    count = len(data)
    total = 0
    for cart in data:
        total += cart.pid.price*cart.quantity
    context ['count'] = count
    context ['total'] = total
    context['profile'] = Profile.objects.get(id = userid)
    return render(request,'confirmorder.html',context)

def addProfile(request):
    if request.method=="GET":
        # userid = request.user.id
        context = {}
        context ['types'] = categories
        return render(request,'profile.html',context)
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        m = request.POST['mobile']
        a = request.POST['address']

    userid = request.user.id
    user = User.objects.filter(id = userid)
    user.update(first_name = fn, last_name = ln)

    profile = Profile.objects.create(id = user[0], mobile = m, address = a)
    profile.save()
    messages.success(request,'Profile Updated Successfully !!')
    return redirect('/')


def makePayment(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    total = 0
    for cart in data:
        total += cart.pid.price*cart.quantity
    client = razorpay.Client(auth=("rzp_test_0JKmrITkTGIvMB", "59dWgJpUw0DlmfY84YtrhAck"))

    data = { "amount": total*100, "currency": "INR", "receipt":"" }
    payment = client.order.create(data=data)
    print(payment)
    context = {}
    context['data'] = payment
    return render(request,'pay.html',context)

def placeOrder(request, ordid):
    '''
    1. userid
    2. cart fetch
    3. insert order details
    4. cart clear
    5. sending gmail
    6. home --> 'order placed'
    '''
    userid = request.user.id
    cartlist = Cart.objects.filter(uid = userid)
    for cart in cartlist:
        order = Order.objects.create(orderid = ordid, userid = cart.uid, pid = cart.pid, quantity = cart.quantity)
        order.save()
    cartlist.delete()
    #sending gmail
    msg = "Thank you for placing the order. Your order id is: "+ordid
    print('receiver email:',request.user.email)
    send_mail(
        "Order placed successfully !!",
        msg,
        "ashwinidkatkar19@gmail.com",
        [request.user.email],
        fail_silently=False
    )
    messages.success(request,'Order Placed Successfully !!')
    return redirect('/')









