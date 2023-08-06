# coding: utf-8
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class CheckToken(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            return Token.objects.get(key=value)
        except Token.DoesNotExist:
            raise serializers.ValidationError('Token not found')
