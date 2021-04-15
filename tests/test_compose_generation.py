from derex.runner.project import Project


def test_generate_ddc_test_compose(complete_project):
    from derex.runner.compose_generation import generate_ddc_test_compose

    with complete_project:
        project = Project()
        compose_file = generate_ddc_test_compose(project)

        assert "cypress" in compose_file.read_text()
        assert project.name in compose_file.read_text()
        assert "/complete/e2e:/e2e" in compose_file.read_text()
