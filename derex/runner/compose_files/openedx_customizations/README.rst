This directory hosts edx-platform customizations intended to be mounted inside the container to override default modules.
This avoid the annoyances of creating an edx-platform fork just to do some minor changes which may, should or are waiting to be merged upstream.
It also provides a mechanism to apply fixes and changes without the need to recreate a base openedx image or to create another edx-platform branch or fork. This proves convenient since we can host all project related customizations in a single place.
