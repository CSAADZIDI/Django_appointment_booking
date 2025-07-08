from rest_framework import serializers
from coach_app.models import CustomUser, TimeSlot, Session

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_coach', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # hashes the password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance

class TimeSlotSerializer(serializers.ModelSerializer):
    end_time = serializers.ReadOnlyField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'is_available']

class SessionSerializer(serializers.ModelSerializer):
    timeslot = TimeSlotSerializer(read_only=True)
    client = CustomUserSerializer(read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'client', 'timeslot', 'subject', 'notes_coach', 'created_at']
