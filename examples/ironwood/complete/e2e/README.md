This Cypress project is an example of how you can run end to end tests in your derex project.

To run the awesome Cypress GUI:

```bash
    export HTTP_PROXY=http://127.0.0.1:80
    npm install cypress
    npx cypress open
```

If you are using [direnv](https://direnv.net/) you can authorize the `.envrc` file to set the `HTTP_PROXY` variable.

More information about installing Cypress can be found on the [official documentation](https://docs.cypress.io/guides/getting-started/installing-cypress.html).

If you instead are happy in just running all your test in a docker container you can use:

```bash
ddc-project run --rm cypress
```

A failing test will make the container exit with code 1.
Since we are mounting the whole cypress project directory inside the container this will likely create `screenshots` and `videos` directories owned by the root user. Hope that's not an issue!
Otherwise you should be able to fix this behavior by [extending the `cypress` service in your local docker-compose.yml file](https://docs.docker.com/compose/extends/).
