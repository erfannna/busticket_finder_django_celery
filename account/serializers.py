from .models import User, Service, InformReport
from rest_framework import serializers
from jalali_date import date2jalali


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name']


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['id', 'name', 'checking_url', 'passengers', 'datetime', 'expired']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['passengers'] = UserSerializer(instance.passengers.all(), many=True).data
        representation['datetime'] = date2jalali(instance.datetime).strftime('%y/%m/%d')
        return representation


class InformSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformReport
        fields = '__all__'
