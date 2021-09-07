class BaseProject:
    """
    The BaseProject defines some common attributes for a project
    and methods to collect informations from loaded project services.

    This will allow Derex Plugins to define additional services and
    specify their requirements, like:

        * start command
        * mounted volumes
        * additional data volumes
        * service specific info (host, credentials)

    All those information might be overridden from the project derex.config.yaml
    file.
    """

    config: dict = {
        "mysql_user": "test_mysql_user",
    }
    name: str = "BaseProject"
    services: list = []
    data_volumes: list = []
    volumes: dict = {}

    @property
    def volumes(self):
        volumes = []
        for module in self.modules:
            volumes.extend(module.volumes)
        return volumes


class BaseService:
    project: Project = None
    name: str = None

    def load(self, project):
        raise NotImplementedError
        print(f"Loading Mysql info on project {project.name}!")
        self.project = project
        project.mysql_user = self.mysql_user(project)
        return


class MysqlService(BaseProjectService):
    def load(self, project):
        print(f"Loading Mysql info on project {project.name}!")
        self.project = project
        project.mysql_user = self.mysql_user(project)
        return

    def mysql_user(self, project) -> str:
        return project.config.get("mysql_user", "mysql")

    @property
    def volumes(self):
        if self.environment is ProjectEnvironment.development:
            mysql_docker_volume = f"derex_{self.mysql_host}"
        else:
            mysql_docker_volume = (
                f"{self.name}_{self.environment.name}_{self.mysql_host}"
            )
        mysql_docker_volume = self.config.get(
            "mysql_docker_volume", mysql_docker_volume
        )

        return [mysql_docker_volume]


class MongodbService(BaseProjectService):
    project = None

    def load(self, project):
        print(f"Loading MongoDB on project {project.name}!")
        self.project = project

        project.mongodb_user = self.mongodb_user(project)

        return project

    def mongodb_user(self, project) -> str:
        return project.config.get("mongodb_user", "default_mongodb")

    @property
    def volumes(self):
        return ["mongodb"]
