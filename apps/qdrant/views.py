from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .search import search


class QdrantSearchView(APIView):
    def post(self, request):
        query = request.data.get('query')
        filter_type = request.data.get('type')
        limit = int(request.data.get('limit', 5))

        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)

        results = search(query, filter_type=filter_type, limit=limit)

        payloads = [
            {
                "payload": r.payload,
                "score": r.score
            } for r in results
        ]

        return Response(payloads, status=status.HTTP_200_OK)
