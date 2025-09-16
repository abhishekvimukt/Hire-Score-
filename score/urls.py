# score/urls.py
from django.urls import path
from .views import OfferView, LeadUploadView, ScoreLeadsView, ResultsView, ResultsCSVView

urlpatterns = [
    path('offer/', OfferView.as_view(), name='set_offer'),
    path('leads/upload/', LeadUploadView.as_view(), name='upload_leads'),
    path('score/', ScoreLeadsView.as_view(), name='score_leads'),
    path('results/', ResultsView.as_view(), name='get_results'),
    path('results/csv/', ResultsCSVView.as_view(), name='get_results_csv'),
]