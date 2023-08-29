from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class SelfRegulatedLearningLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 一個用戶可以有多個自主學習日誌
    learning_goal = models.TextField() # 可以存儲學習目標的文本
    goal_progress = models.JSONField() # 可以存儲雷達圖的數據
    daily_learning_time = models.DurationField() # 可以存儲每日學習時間
    weekly_learning_time = models.DurationField() # 可以存儲每週學習時間
    monthly_learning_time = models.DurationField() # 可以存儲每月學習時間
    answer_speed = models.FloatField() # 可以存儲答題速度
    question_count = models.IntegerField() # 可以存儲答題數量
    correct_answer_rate = models.FloatField() # 可以存儲答題正確率
    activity_distribution = models.JSONField() # 可以存儲不同學習活動的時間分布
    performance_tracking = models.JSONField() # 可以存儲學習成效的數據，例如測驗分數、作業評分等

class CollaborativeLearningLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 一個用戶可以有多個協作學習日誌
    social_interaction = models.JSONField() # 可以存儲網絡圖的數據
    community_resource_usage = models.JSONField() # 可以存儲學習者利用社群資源的情況
    community_influence = models.JSONField() # 可以存儲學習者在社群中的影響力數據
    community_participation = models.JSONField() # 可以存儲學習者在社群中的參與度數據
