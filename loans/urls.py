from django.urls import path
from .views import LoanOverviewView, LoanCreateView, LoanSimulationView, LoanDetailView

urlpatterns = [
    path('', LoanOverviewView.as_view()),               
    path('create/', LoanCreateView.as_view()),           
    path('simulation/', LoanSimulationView.as_view()),   
    path('<int:pk>/', LoanDetailView.as_view()),         
]