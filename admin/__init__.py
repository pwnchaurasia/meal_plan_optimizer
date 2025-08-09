# from sqladmin import ModelView
# from db.models.user import User, UserProfile
#
# class BaseAdmin(ModelView):
#     pass
#
# models = [User, UserProfile]
#
# admin_views = []
# for model in models:
#     class_name = f"{model.__name__}Admin"
#     admin_class = type(class_name, (BaseAdmin,), {"model": model})
#     admin_views.append(admin_class)
