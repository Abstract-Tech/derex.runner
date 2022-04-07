function login(email, password) {
  cy.request({
    url: Cypress.env("LOGIN_URL"),
    failOnStatusCode: false,
  });
  // Save CSRFtoken and use it in header to send login POST request
  cy.getCookie("csrftoken")
    .its("value")
    .then(($token) => {
      cy.request({
        method: "POST",
        url: Cypress.env("LOGIN_URL"),
        form: true,
        body: {
          email: email,
          password: password,
          remember: false,
        },
        headers: {
          Referer: Cypress.env("LMS_URL"),
          "X-CSRFToken": $token,
        },
      });
    });
}

Cypress.Commands.add("login_staff", () => {
  login(Cypress.env("staff_user").email, Cypress.env("staff_user").password);
});

Cypress.Commands.add("login_learner", () => {
  login(
    Cypress.env("learner_user").email,
    Cypress.env("learner_user").password
  );
});

Cypress.Commands.add("createCourse", (next_url) => {
  cy.visit(Cypress.env("CMS_URL"));

  function makeChar(length) {
    let result = "";
    let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  }

  // Generate some random values
  let course_name = "Test " + Math.floor(Math.random() * 100000);
  let course_org = makeChar(6);
  let course_number = makeChar(2) + Math.floor(Math.random() * 1000);
  let course_run = new Date().getFullYear();

  cy.get(".nav-actions .new-course-button").wait(500).click();
  // Fill and submit the form
  cy.get("#new-course-name").type(course_name);
  cy.get("#new-course-org").type(course_org);
  cy.get("#new-course-number").type(course_number);
  cy.get("#new-course-run").type(course_run);
  cy.get("#create-course-form > .actions > .action-primary").click();

  // Wait for the form to redirect
  cy.url().should("contain", "/course/");

  if (next_url) {
    cy.visit(next_url);
  }
});

Cypress.Commands.add("fileUpload", (fileName) => {
  cy.fixture(fileName, "binary")
    .then(Cypress.Blob.binaryStringToBlob)
    .then((fileContent) => {
      cy.get("input[type=file").attachFile({
        fileContent,
        filePath: fileName,
        encoding: "utf-8",
        lastModified: new Date().getTime(),
      });
    });
});
