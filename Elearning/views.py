from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from app.models import Categories,Course,Level,Video,UserCourse,Payment,Review
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
import razorpay
from django.views.decorators.csrf import csrf_exempt

from .settings import *
from time import time
from django.core.mail import send_mail


client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))



def BASE(request):
    return render(request,'base.html')


def HOME(request):
    category = Categories.objects.all().order_by('id')[0:6]
    course = Course.objects.filter(status = 'PUBLISH').order_by('-id')
    courses = Course.objects.all()
    print(course)

    context = {
        'category':category,
        'course':course,
        'courses': courses
    }

    return render(request,'Main/home.html',context)


def SINGLE_COURSE(request):
    category = Categories.get_all_category(Categories)
    level = Level.objects.all()
    course = Course.objects.all()
    FreeCourse_count =Course.objects.filter(price = 0).count()
    PaidCourse_count = Course.objects.filter(price__gte=1).count()


    context ={
        'category':category,
        'level':level,
        'course':course,
        'FreeCourse_count':FreeCourse_count,
        'PaidCourse_count':PaidCourse_count
    }

    return render(request,'Main/single_course.html',context)

def filter_data(request):
    category = request.GET.getlist('category[]')
    level = request.GET.getlist('level[]')
    price = request.GET.getlist('price[]')
    print(price)

    if price == ['PriceFree']:
        course = Course.objects.filter(price=0)
    elif price == ['PricePaid']:
        course = Course.objects.filter(price__gte=1)
    elif price == ['PriceAll']:
        course = Course.objects.all()
    elif category:
        course = Course.objects.filter(category__id__in = category).order_by('-id')
    elif level:
        course = Course.objects.filter(level__id__in=level).order_by('-id')
    else:
        course = Course.objects.all().order_by('-id')

    context ={
        'course':course
    }
    t = render_to_string('ajax/course.html',context)
    return JsonResponse({'data': t})
def CONTACT_US(request):
    category = Categories.get_all_category(Categories)

    context ={
        'category':category
    }

    return render(request,'Main/contact_us.html',context)


def ABOUT_US(request):
    category = Categories.get_all_category(Categories)
    reviews = Review.objects.order_by('-date_added')[:3]

    context = {
        'category': category,
        'reviews': reviews
    }
    return render(request,'Main/about_us.html',context)



def SEARCH_COURSE(request):
    category = Categories.get_all_category(Categories)

    query = request.GET['query']
    course = Course.objects.filter(title__icontains = query)
    print(course)

    context ={
        'course':course,
        'category': category
    }
    return render(request,'search/search.html',context)




def COURSE_DETAILS(request,slug):
    category = Categories.get_all_category(Categories)
    time_duration = Video.objects.filter(course__slug = slug).aggregate(sum=Sum('time_duration'))

    course = get_object_or_404(Course, slug=slug)
    courses = Course.objects.all()
    if request.user.is_authenticated:
        user_id = request.user.id
        try:
            check_enroll = UserCourse.objects.get(user_id=user_id, course=course)
        except UserCourse.DoesNotExist:
            check_enroll = None

    else:
        check_enroll = None

    context ={
        'course':course,
        'category': category,
        'time_duration':time_duration,
        "courses":courses,
        'check_enroll':check_enroll
    }
    return render(request,'course/course_details.html',context)


def PAGE_NOT_FOUND(request):
    category = Categories.get_all_category(Categories)

    context = {
        'category': category
    }
    return render(request,'error/404.html',context)

@login_required
def CHECKOUT(request,slug):
    course = Course.objects.get(slug = slug)
    action = request.GET.get('action')
    order = None
    if course.price == 0:
        course = UserCourse(
            user = request.user,
            course = course,
        )
        course.save()
        messages.success(request,'Course Are Succesfully Enrolled...!')
        return redirect('my_course')

    elif action == 'create_payment':
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            country = request.POST.get('country')
            address_1 = request.POST.get('address_1')
            address_2 = request.POST.get('address_2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postcode = request.POST.get('postcode')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            order_comments = request.POST.get('order comments')

            amount_cal = course.price - (course.price * course.discount / 100)
            amount = int (amount_cal)* 100
            currency = "INR"
            notes = {
                "name": f'{first_name} {last_name}',
                "country": country,
                "address": f'{address_1} {address_2}',
                "city": city,
                "state": state,
                "postcode": postcode,
                "phone": phone,
                "email": email,
                "order_comments": order_comments,
            }
            receipt = f"SKola-{int(time())}"
            order = client.order.create(
                {
                    'receipt': receipt,
                    'notes': notes,
                    'amount': amount,
                    'currency': currency,
                }
            )
            payment = Payment(
                course=course,
                user=request.user,
                order_id=order.get('id')
            )
            payment.save()


    context={
        'course':course,
        'order':order
    }
    return render(request,'checkout/checkout.html',context)

@login_required
def MY_COURSE(request):
    course = UserCourse.objects.filter(user = request.user)


    context = {
        'course':course,
    }
    return render(request,'course/my-course.html',context)


@csrf_exempt
def VERIFY_PAYMENT(request):
    if request.method == "POST":
        data = request.POST
        try:
            client.utility.verify_payment_signature(data)
            razorpay_order_id = data['razorpay_order_id']
            razorpay_payment_id = data['razorpay_payment_id']

            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = True

            usercourse = UserCourse(
                user=payment.user,
                course=payment.course,
            )
            usercourse.save()
            payment.user_course = usercourse
            payment.save()

            context = {
                'data': data,
                'payment': payment,
            }
            return render(request, 'verify_payment/success.html', context)
        except:
            return render(request, 'verify_payment/fail.html')

def VERIFY_PAYMENT_SUCCESS(request):
    return render(request,'verify_payment/success.html')

@login_required
def home(request):
   context = {}
   return render(request, 'home.html', context)


def redirect_to_course(request, slug):
  return redirect('course_details', slug=slug)


def WATCH_COURSE(request,slug):
    course = get_object_or_404(Course, slug=slug)
    lecture = request.GET.get('lecture')
    video = Video.objects.get(id=lecture)



    context = {
        'course': course,
        'video':video,
    }
    return render(request,'course/watch-course.html',context)


@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        review = Review(course=course, user=request.user)
        review.rating = request.POST.get('rating')
        review.title = request.POST.get('title')
        review.content = request.POST.get('content')

        if 'profile_img' in request.FILES:
            review.profile_img = request.FILES['profile_img']

        review.save()
        return redirect('course_details', slug=slug)

    return redirect('course_details', slug=slug)


def sendmail(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        send_mail(
            name,
            message,
            email,
            ['bhuravanepritesh@gmail.com'],
            fail_silently=False
        )

        return redirect('contact_us')

    return redirect('contact_us')

def logout_view(request):
    logout(request)
    return redirect('home')

