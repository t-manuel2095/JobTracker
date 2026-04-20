from rest_framework import serializers
from .models import JobApplication, StatusHistory

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = JobApplication
        fields = ['id', 'user', 'company', 'role', 'status', 'applied_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        updated_instance = super().update(instance, validated_data)

        if(old_status != new_status):
            StatusHistory.objects.create(
                job = updated_instance,
                old_status = old_status,
                new_status = new_status,
            )

        return updated_instance

class StatusHistorySerializer(serializers.ModelSerializer): 
    class Meta: 
        model = StatusHistory
        fields = ['id', 'job', 'old_status','new_status', 'changed_at']
        read_only_fields = ['id', 'job', 'old_status','new_status', 'changed_at']

class JobStatsSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    status_breakdown = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Count of applications by status"
    )
    status_percentages = serializers.DictField(
        child=serializers.FloatField(),
        help_text="Percentage of applications by status"
    )
    offers = serializers.IntegerField()
    rejections = serializers.IntegerField()
    interviews = serializers.IntegerField()
    success_rate_percentage = serializers.FloatField()
    rejection_rate_percentage = serializers.FloatField()

class DetailedStatsSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    status_breakdown = serializers.DictField(child=serializers.IntegerField())
    status_percentages = serializers.DictField(child=serializers.FloatField())
    applications_by_month = serializers.ListField(child=serializers.DictField())
    average_days_to_interview = serializers.FloatField()
    average_days_to_offer = serializers.FloatField()
    success_rate_percentage = serializers.FloatField()
    rejection_rate_percentage = serializers.FloatField()