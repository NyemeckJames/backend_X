from django.urls import path
from .views import SignUpView, LoginView, create_checkout_session,RegisterEventView, PaymentSuccess, GetUserByID

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("create_checkout_session/", create_checkout_session, name="create_checkout_session"),
    path("payment-success/<str:session_id>/", PaymentSuccess.as_view(), name="create_checkout_session"),
    path("register-event/<int:event_id>/", RegisterEventView.as_view(), name="create_checkout_session"),
    path("get-user-by-id/<int:user_id>/", GetUserByID.as_view(), name="get_user_by_id"),
]
