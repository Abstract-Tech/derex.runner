# -*- coding: utf-8 -*-
"""Tests for `derex.runner` package."""

from .test_cli import assert_result_ok
from click.testing import CliRunner
from derex.runner.cli import ddc
from derex.runner.cli import ddc_local
from derex.runner.docker import execute_mysql_query
from derex.runner.project import Project
from pathlib import Path

import docker
import os
import pytest
import shutil
import tarfile
import urllib3


BACKUP_PROJ = Path(__file__).with_name("fixtures") / "backup"
runner = CliRunner()


@pytest.mark.slowtest
def test_ddc_local_backup_restore(workdir):
    with workdir(BACKUP_PROJ):
        project = Project()

        # Setup
        # Download the Demo course
        demo_course_url = "https://github.com/edx/edx-demo-course/archive/open-release/ironwood.2.tar.gz"
        demo_course_file = BACKUP_PROJ / "Demo-course.tar.gz"
        demo_course_dir = BACKUP_PROJ / "Demo-course"

        if not os.path.isfile(demo_course_file):
            http = urllib3.PoolManager()
            response = http.request("GET", demo_course_url, preload_content=False)

            with open(demo_course_file, "wb") as out:
                while True:
                    data = response.read(6 * 1024)
                    if not data:
                        break
                    out.write(data)

        if not os.path.isdir(demo_course_dir):
            # Extract the demo course
            tar = tarfile.open(demo_course_file, "r:gz")
            tar.extractall(demo_course_dir)
            tar.close()

        # Ensure mongodb and mysql services are up
        runner.invoke(ddc, ["up", "-d"])

        # Load the demo course in the mongodb database
        result = runner.invoke(
            ddc_local,
            [
                "run",
                "--rm",
                "-v",
                f"{demo_course_dir}:/demo-course",
                "lms",
                "python",
                "manage.py",
                "lms",
                "import",
                "/demo-course",
            ],
        )
        assert_result_ok(result)

        # Load some fixtures in the mysql database
        result = runner.invoke(
            ddc_local,
            [
                "run",
                "--rm",
                "-v",
                f"{project.fixtures_dir}:/demo-course",
                "lms",
                "python",
                "manage.py",
                "lms",
                "import",
                "/demo-course",
            ],
        )
        assert_result_ok(result)

        # Run a dump
        result = runner.invoke(ddc_local, ["backup-dump"])
        assert_result_ok(result)

        # Reset all data
        # TODO: reset also mongodb data
        execute_mysql_query(f"DROP DATABASE {project.mysql_db_name}")
        assert_result_ok(result)

        # Run a restore
        result = runner.invoke(ddc_local, ["backup-restore"], input="0\n0")
        assert_result_ok(result)

        # Test that a user exist
        script = """from django.contrib.auth.models import User;\
        user = User.objects.get(pk=3);\
        assert user.email == 'user@example.com'\
        """
        result = runner.invoke(
            ddc_local,
            ["run", "--rm", "lms", "python", "manage.py", "lms", "shell", "-c", script],
        )
        assert result.exit_code == 0

        # Test that the demo course exists
        script = """from xmodule.modulestore.django import modulestore;\
        from opaque_keys.edx.keys import CourseKey;\
        modulestore = modulestore();\
        course_key = CourseKey.from_string('course-v1:edX+DemoX+Demo_Course');\
        assert modulestore.has_course(course_key);\
        """
        result = runner.invoke(
            ddc_local,
            ["run", "--rm", "lms", "python", "manage.py", "lms", "shell", "-c", script],
        )
        assert result.exit_code == 0
