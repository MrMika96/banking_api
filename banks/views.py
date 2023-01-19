from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from banks.models import Bank
from banks.serializers import BanksSerializer


class BanksViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    pagination_class = None
    serializer_class = BanksSerializer
    permission_classes = [IsAuthenticated]
