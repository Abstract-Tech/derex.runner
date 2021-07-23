ELASTIC_SEARCH_CONFIG = [
    {
        "host": "elasticsearch",
        "port": 9200,
        "use_ssl": False,
    }  # noqa: E231
]
if DEREX_OPENEDX_VERSION == "lilac":
    ELASTIC_SEARCH_CONFIG[0]["host"] = "elasticsearch7"

SEARCH_ENGINE = "search.elastic.ElasticSearchEngine"
SEARCH_INITIALIZER = (
    "lms.lib.courseware_search.lms_search_initializer.LmsSearchInitializer"
)
SEARCH_RESULT_PROCESSOR = (
    "lms.lib.courseware_search.lms_result_processor.LmsSearchResultProcessor"
)
SEARCH_FILTER_GENERATOR = (
    "lms.lib.courseware_search.lms_filter_generator.LmsSearchFilterGenerator"
)

FEATURES["ENABLE_COURSEWARE_INDEX"] = True
FEATURES["ENABLE_LIBRARY_INDEX"] = True
FEATURES["ENABLE_DASHBOARD_SEARCH"] = True
FEATURES["ENABLE_COURSEWARE_SEARCH"] = True
FEATURES["ENABLE_COURSE_DISCOVERY"] = False
COURSE_DISCOVERY_FILTERS = ["org", "language", "modes"]
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True
