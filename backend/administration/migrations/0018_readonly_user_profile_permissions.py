from django.db import migrations


def grant_readonly_user_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        readonly_group = Group.objects.get(name="Readonly")
    except Group.DoesNotExist:
        return

    perms = Permission.objects.filter(
        content_type__app_label="auth",
        content_type__model="user",
        codename__in=["view_user", "change_user"],
    )
    readonly_group.permissions.add(*perms)


def revoke_readonly_user_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        readonly_group = Group.objects.get(name="Readonly")
    except Group.DoesNotExist:
        return

    perms = Permission.objects.filter(
        content_type__app_label="auth",
        content_type__model="user",
        codename__in=["view_user", "change_user"],
    )
    readonly_group.permissions.remove(*perms)


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0017_create_auth_groups"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            grant_readonly_user_permissions,
            reverse_code=revoke_readonly_user_permissions,
        ),
    ]
