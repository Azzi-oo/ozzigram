from django.contrib import admin
from general.models import (
    User,
    Post,
    Comment,
    Reaction,
)
from django.contrib.auth.models import Group
from rangefilter.filters import DateRangeFilter


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    readonly_fields = (
        "date_joined",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("date_joined", DateRangeFilter),
    )
    fieldsets = (
        (
            "Личные данные", {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            }
        ),
        (
            "Учетные данные", {
                "fields": (
                    "username",
                    "password",
                )
            }
        ),
        (
            "Статусы", {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            }
        ),
        (
            None, {
                "fields": (
                    "friends",
                )
            }
        ),
        (
            "Даты", {
                "fields": (
                    "date_joined",
                    "last_login",
                )

            }
        )
    )
    search_fields = (
        "id",
        "username",
        "email",
    )


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "title",
        "body",
        "created_at",
    )

    def get_body(self, obj):
        max_length = 64
        if len(obj.body) > max_length:
            return obj.body[:61] + "..."
        return obj.body
    get_body.short_description = "body"

    def get_comment_count(self, obj):
        return obj.comments.count()

    fields = (
        "date_joined",
    )
    search_fields = (
        "id",
        "title",
        "author__username",
    )
    list_filter = (
        ("created_at", DateRangeFilter),
    )



@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "body",
        "created_at",
    )
    list_display_links = (
        "id",
        "body",
    )
    readonly_fields = (
        "created_at",
    )
    search_fields = (
        "author__username",
        "post__title",
    )


@admin.register(Reaction)
class ReactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "value",
    )
    list_filter = ("value", )
    search_fields = ("author__username", "post__title")


admin.site.unregister(Group)
