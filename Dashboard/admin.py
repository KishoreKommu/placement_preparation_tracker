from django.contrib import admin
from .models import Skill, MockTest, MockTestQuestion, Company, CareerPath


# =========================
# Skill Admin
# =========================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "level")
    list_filter = ("level",)
    search_fields = ("name",)
    ordering = ("name",)


# =========================
# Mock Test Question Inline
# =========================
class MockTestQuestionInline(admin.TabularInline):
    model = MockTestQuestion
    extra = 1


# =========================
# Mock Test Admin
# =========================
@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    inlines = [MockTestQuestionInline]


# =========================
# Mock Test Question Admin
# =========================
@admin.register(MockTestQuestion)
class MockTestQuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "question", "answer")
    search_fields = ("question",)
    list_filter = ("test",)


# =========================
# Company Admin
# =========================
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "skillset", "positions")
    search_fields = ("name", "skillset")
    list_filter = ("positions",)


# =========================
# Career Path Admin
# =========================
@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at",)


from django.contrib import admin
from .models import Skill, MockTest, MockTestQuestion, Company, CareerPath, Opportunity, SavedOpportunity

# @admin.register(Opportunity)
# class OpportunityAdmin(admin.ModelAdmin):
#     list_display = ("title", "company_name", "opp_type", "tier", "package_details", "deadline", "is_active")
#     list_filter = ("opp_type", "tier", "is_active", "deadline")
#     search_fields = ("title", "company_name", "requirements")


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "opp_type", "tier", "package_details", "deadline", "is_active")
    list_filter = ("opp_type", "tier", "is_active", "deadline")
    search_fields = ("title", "company_name", "requirements")
    actions = ['mark_as_inactive', 'mark_as_active']

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)