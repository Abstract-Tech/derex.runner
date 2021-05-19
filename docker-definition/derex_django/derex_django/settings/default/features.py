FEATURES.update(
    {
        "ALLOW_ALL_ADVANCED_COMPONENTS": True,
        "ALLOW_COURSE_STAFF_GRADE_DOWNLOADS": True,
        "ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER": False,
        "CERTIFICATES_ENABLED": True,
        "CERTIFICATES_HTML_VIEW": True,
        "CERTIFICATES_INSTRUCTOR_GENERATION": True,
        "DISABLE_STUDIO_SSO_OVER_LMS": False,
        "ENABLE_COMBINED_LOGIN_REGISTRATION": True,
        "ENABLE_COMBINED_LOGIN_REGISTRATION_FOOTER": False,
        "ENABLE_CORS_HEADERS": True,
        "ENABLE_DISCUSSION_SERVICE": False,
        "ENABLE_GRADE_DOWNLOADS": True,
        "ENABLE_OAUTH2_PROVIDER": True,
        "ENABLE_PREREQUISITE_COURSES": True,
        "ENABLE_SPECIAL_EXAMS": True,
        "ENABLE_SYSADMIN_DASHBOARD": True,
        "MILESTONES_APP": True,
    }
)

DEFAULT_COURSE_VISIBILITY_IN_CATALOG = "both"
COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# Remove CSMH as discussed in
# https://discuss.openedx.org/t/new-edxapp-csmh-mysql-database-in-juniper/2127
FEATURES["ENABLE_CSMH_EXTENDED"] = False
for coursewarehistoryextended_app in [
    "coursewarehistoryextended",
    "lms.djangoapps.coursewarehistoryextended",
]:
    if coursewarehistoryextended_app in INSTALLED_APPS:
        INSTALLED_APPS.remove(coursewarehistoryextended_app)

DATABASE_ROUTERS.remove(
    "openedx.core.lib.django_courseware_routers.StudentModuleHistoryExtendedRouter"
)
