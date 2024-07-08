from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from .forms import *


def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {
        "categories": categories,
        "products": products,
        "title": "Главная страница"
    }
    return render(request, "index.html", context)


def sort_products_by_category_view(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        messages.error(request, "Категория не найдена")
        return redirect('index')

    products = Product.objects.filter(category=category_id)
    context = {
        "title": f"Категория: {category.title}",
        "products": products,
        "category": category
    }
    return render(request, "category_page.html", context)


def product_detail_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Товар не найден")
        return redirect('index')

    rating_range = range(1, 6)
    context = {
        "product": product,
        'rating_range': rating_range,
        "title": product.title
    }
    return render(request, "product_detail.html", context)


def search_view(request):
    word = request.GET.get("q")
    products = Product.objects.filter(title__iregex=word)
    context = {
        "title": "Результаты поиска",
        "products": products
    }
    return render(request, "search.html", context)


def user_login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, "Вы успешно вошли в аккаунт!")
                return redirect('index')
            else:
                messages.error(request, "Логин или пароль неправильный!")
                return redirect('login')
        else:
            messages.error(request, "Логин или пароль неправильный!")
            return redirect('login')
    else:
        form = UserLoginForm()
    context = {
        "title": "Вход в аккаунт",
        "form": form
    }
    return render(request, "login.html", context)


def user_registration_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(user=user)
            profile.save()
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('login')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
            return redirect('registration')
    else:
        form = UserRegistrationForm()
    context = {
        "title": "Регистрация",
        "form": form
    }
    return render(request, "registration.html", context)


def user_logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли с аккаунта!")
    return redirect('index')


def check_profile_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Пользователь не найден")
        return redirect('index')

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "Профиль не найден")
        return redirect('index')

    context = {
        "profile": profile,
        "title": "Профиль пользователя"
    }
    return render(request, "profile.html", context)


def change_profile_data(request, user_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для выполнения этого действия.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Пользователь не найден")
        return redirect('index')

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "Профиль не найден")
        return redirect('index')

    if request.method == "POST":
        user_form = UserForm(instance=user, data=request.POST)
        profile_form = ProfileForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            messages.success(request, "Данные успешно изменены")
            return redirect("profile", user.id)
        else:
            for field in user_form.errors:
                messages.error(request, user_form.errors[field].as_text())
            for field in profile_form.errors:
                messages.error(request, profile_form.errors[field].as_text())
            return redirect('change_profile', user.id)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        "title": "Изменить профиль",
        "user_form": user_form,
        "profile_form": profile_form
    }
    return render(request, "change_profile.html", context)


def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для просмотра корзины")
        return redirect('login')

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total_item_price = item.product.price * item.quantity
    total_price = sum(item.total_item_price for item in cart_items)
    context = {
        "title": "Корзина",
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "cart.html", context)


def add_to_cart_view(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для добавления товара в корзину")
        return redirect('login')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('cart')

    quantity = int(request.POST.get('quantity', 1))
    try:
        cart_item = CartItem.objects.get(user=request.user, product=product)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(user=request.user, product=product, quantity=quantity)

    messages.success(request, 'Товар добавлен в корзину')
    return redirect('cart')


def remove_from_cart_view(request, cart_item_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для удаления товара из корзины")
        return redirect('login')

    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        messages.error(request, 'Товар в корзине не найден')
        return redirect('cart')

    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart')


def update_cart_item_view(request, cart_item_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для изменения количества товара")
        return redirect('login')

    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        messages.error(request, "Товар в корзине не найден")
        return redirect('cart')

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity"))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Количество товара обновлено')
            else:
                messages.error(request, 'Количество должно быть больше нуля')
        except ValueError:
            messages.error(request, 'Некорректное значение количества')

    return redirect('cart')


def favorites_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для просмотра Избранного")
        return redirect('login')

    favorite_items = FavoriteItem.objects.filter(user=request.user)
    context = {
        "title": "Избранное",
        "favorite_items": favorite_items
    }
    return render(request, "favorites.html", context)


def add_to_favorites_view(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для добавления товара в Избранное")
        return redirect('login')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('favorites')

    try:
        favorite_item = FavoriteItem.objects.get(user=request.user, product=product)
        messages.info(request, 'Товар уже в избранном.')
    except FavoriteItem.DoesNotExist:
        FavoriteItem.objects.create(user=request.user, product=product)
        messages.success(request, 'Товар добавлен в избранное.')

    return redirect('favorites')


def remove_from_favorites_view(request, favorite_item_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для удаления товара из Избранного")
        return redirect('login')

    try:
        favorite_item = FavoriteItem.objects.get(id=favorite_item_id, user=request.user)
    except FavoriteItem.DoesNotExist:
        messages.error(request, 'Товар в избранном не найден')
        return redirect('favorites')

    favorite_item.delete()
    messages.success(request, 'Товар удален из избранного')
    return redirect('favorites')


def add_review_view(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для добавления отзыва к товару")
        return redirect('login')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('index')

    if request.method == "POST":
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Ваш отзыв добавлен')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        "title": f"Добавить отзыв к {product.title}",
        "form": form,
        "product": product,
        "rating_range": range(1, 6)
    }
    return render(request, "add_review.html", context)


def order_create_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для оформления заказа")
        return redirect('login')

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, price=item.product.price,
                                         quantity=item.quantity)
            cart_items.delete()
            messages.success(request, "Ваш заказ был успешно оформлен!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = OrderCreateForm()

    context = {
        'title': "Оформление заказа",
        'form': form,
        'cart_items': cart_items,
        'total_price': sum(item.product.price * item.quantity for item in cart_items)
    }
    return render(request, 'order_create.html', context)


def order_confirmation_view(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "Пожалуйста, войдите в аккаунт для подтверждения заказа")
        return redirect('login')

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Заказ не найден")
        return redirect('index')

    context = {
        'title': "Ваш заказ",
        'order': order
    }
    return render(request, 'order_confirmation.html', context)
