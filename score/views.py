# score/views.py
import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.http import HttpResponse
from .models import Offer, Lead, ScoreResult
from .serializers import OfferSerializer, LeadSerializer, ScoreResultSerializer, FileUploadSerializer
from .scoring import get_final_score_and_intent

# In-memory storage (replace with a database/cache in production)
# DB = {
#     "offer": None,
#     "leads": [],
#     "results": []
# }

class OfferView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            return Response({"message": f"Offer '{offer.name}' set successfully.", "offer_id": offer.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeadUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser,)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.csv'):
            return Response({"error": "Please upload a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        leads_data = [row for row in reader]
        if not leads_data:
            return Response({"error": "CSV file is empty or malformed."}, status=status.HTTP_400_BAD_REQUEST)

        # Use LeadSerializer to validate and save leads
        lead_serializer = LeadSerializer(data=leads_data, many=True)
        if lead_serializer.is_valid():
            lead_serializer.save()
            return Response({"message": f"Successfully uploaded {len(leads_data)} leads."}, status=status.HTTP_201_CREATED)
        return Response(lead_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScoreLeadsView(APIView):
    def post(self, request, *args, **kwargs):
        # Expect an offer_id in the request body to link scores to a specific offer
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response({"error": "Please provide an 'offer_id' to score leads against."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer = Offer.objects.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        leads = Lead.objects.all()
        if not leads.exists():
            return Response({"error": "No leads uploaded. Please POST to /leads/upload/ first."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clear previous score results for this offer (optional, depending on desired behavior)
        ScoreResult.objects.filter(offer=offer).delete()

        results_data = []
        for lead in leads:
            # Assuming get_final_score_and_intent from scoring.py takes lead and offer objects
            score_data = get_final_score_and_intent(lead, offer)
            
            # Create ScoreResult entry
            score_result = ScoreResult.objects.create(
                offer=offer,
                lead=lead,
                intent=score_data['intent'],
                score=score_data['score'],
                reasoning=score_data['reasoning']
            )
            results_data.append(ScoreResultSerializer(score_result).data)
            
        return Response({"message": f"Successfully scored {len(results_data)} leads.", "results": results_data}, status=status.HTTP_200_OK)

class ResultsView(APIView):
    def get(self, request, *args, **kwargs):
        offer_id = request.query_params.get('offer_id')
        if not offer_id:
            return Response({"error": "Please provide an 'offer_id' to retrieve results."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            offer = Offer.objects.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        results = ScoreResult.objects.filter(offer=offer).select_related('lead')
        if not results.exists():
            return Response({"message": "No results found for this offer. Please run the /score/score/ endpoint first."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ScoreResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ResultsCSVView(APIView):
    def get(self, request, *args, **kwargs):
        offer_id = request.query_params.get('offer_id')
        if not offer_id:
            return Response({"error": "Please provide an 'offer_id' to export results."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            offer = Offer.objects.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        results = ScoreResult.objects.filter(offer=offer).select_related('lead')
        if not results.exists():
            return Response({"message": "No results found to export for this offer."}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare data for CSV export
        data = []
        for result in results:
            data.append({
                "name": result.lead.name,
                "role": result.lead.role,
                "company": result.lead.company,
                "intent": result.intent,
                "score": result.score,
                "reasoning": result.reasoning
            })

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="scored_leads_{offer.id}.csv"'
        
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return response