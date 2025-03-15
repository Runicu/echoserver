from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import Book, CustomUser, Order, OrderItem
from .forms import BookForm, CustomUserCreationForm, CustomUserChangeForm
from django.http import JsonResponse, HttpResponseRedirect

def is_admin(user):
    return user.role == "admin"

def remove_from_cart(request, pk):
    cart = request.COOKIES.get('cart', '')
    if cart:
        cart = cart.split(',')
        if str(pk) in cart:
            cart.remove(str(pk))

    response = redirect('view_cart')
    response.set_cookie('cart', ','.join(cart))
    return response

def checkout(request):
    cart = request.COOKIES.get('cart', '')
    if not cart:
        return redirect('view_cart')

    cart = cart.split(',')
    books = Book.objects.filter(id__in=cart)

    user = request.user if request.user.is_authenticated else None

    order = Order.objects.create(
        user=user,
        total_price=sum(book.price for book in books)
    )

    for book in books:
        OrderItem.objects.create(
            order=order,
            book=book,
            price=book.price,
            quantity=1
        )

    response = redirect('view_orders')
    response.delete_cookie('cart')
    return response


def view_orders(request):
    orders = Order.objects.filter(user=request.user) if request.user.is_authenticated else Order.objects.filter(user__isnull=True)
    return render(request, 'bookstore_app/orders.html', {'orders': orders})

def view_cart(request):
    cart = request.COOKIES.get('cart', '')
    if cart:
        cart = cart.split(',')
        books = Book.objects.filter(id__in=cart)
    else:
        books = []

    total_price = sum(book.price for book in books)

    return render(request, 'bookstore_app/cart.html', {'books': books, 'total_price': total_price})

def add_to_cart(request, pk):
    cart = request.COOKIES.get('cart', '')
    if cart:
        cart = cart.split(',')
    else:
        cart = []

    if str(pk) not in cart:
        cart.append(str(pk))

    response = HttpResponseRedirect('/')
    response.set_cookie('cart', ','.join(cart))
    return response

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'bookstore_app/profile.html', {'form': form})


def check_username(request):
    username = request.GET.get('username', None)

    if username and CustomUser.objects.filter(username=username).exists():
        return JsonResponse({'is_unique': False})
    return JsonResponse({'is_unique': True})

def logout(request):
    auth_logout(request)
    return redirect('book_list')

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'bookstore_app/signup.html', {'form': form})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('book_list')
        else:
            error_message = "Invalid username or password"
            return render(request, 'bookstore_app/login.html', {'error_message': error_message})
        
    return render(request, 'bookstore_app/login.html')

def book_list(request):
    title = request.GET.get('title', '')
    author = request.GET.get('author', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    books = Book.objects.all()

    if title:
        books = books.filter(title__icontains=title)
    if author:
        books = books.filter(author__icontains=author)
    if price_min:
        books = books.filter(price__gte=price_min)
    if price_max:
        books = books.filter(price__lte=price_max)

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bookstore_app/book_list.html', {'page_obj': page_obj})

@login_required
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'bookstore_app/book_form.html', {'form': form})

@login_required
@user_passes_test(is_admin, login_url='book_list')
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)

    return render(request, 'bookstore_app/book_form.html', {'form': form})

@login_required
@user_passes_test(is_admin, login_url='book_list')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.delete()
        return redirect('book_list')
    
    return render(request, 'bookstore_app/book_confirm_delete.html', {'book': book})
