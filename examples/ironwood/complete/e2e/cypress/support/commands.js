// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add("login", (email, password) => {
  const login_url = Cypress.env("LMS_URL") + "/login_ajax";
  // Open the login page to get a CSRF cookie
  cy.request({
    url: login_url,
    failOnStatusCode: false,
  });

  // Save csrftoken and use it in header to send Login Post request
  cy.getCookie("csrftoken")
    .its("value")
    .then(($token) => {
      let response = cy.request({
        method: "POST",
        url: login_url,
        form: true,
        body: {
          email: email,
          password: password,
          remember: false,
        },
        headers: {
          Referer: login_url,
          "X-CSRFToken": $token,
        },
      });
    });
});

Cypress.on("uncaught:exception", (e, runnable) => {
  console.log("error", e);
  console.log("runnable", runnable);
  cy.log("caught error", e);
  return false;
});

Cypress.Commands.add("importCourse", (coursePath) => {
  cy.wait(2000);
  cy.fixture(coursePath, "base64").as("uploadedCourse");
  cy.get("#fileupload input[type=file]").then(function ($input) {
    // convert the logo base64 string to a blob
    return Cypress.Blob.base64StringToBlob(this.uploadedCourse).then((blob) => {
      const testFile = new File([blob], "course.tar.gz", {
        type: "application/tar+gzip",
      });
      let dataTransfer = new window.DataTransfer();
      dataTransfer.items.add(testFile);
      $input[0].files = dataTransfer.files;
      cy.wrap($input).trigger("change", { force: true });
    });
  });
});

Cypress.Commands.add("uploadFile", (coursePath) => {
  cy.wait(2000);
  cy.fixture(coursePath, "base64").as("uploadedCourse");
  cy.get("#fileupload").then(function ($input) {
    // convert the logo base64 string to a blob
    return Cypress.Blob.base64StringToBlob(this.uploadedCourse).then((blob) => {
      const testFile = new File([blob], "course.tar.gz", {
        type: "application/tar+gzip",
      });
      let dataTransfer = new window.DataTransfer();
      dataTransfer.items.add(testFile);
      $input[0].files = dataTransfer.files;
      cy.wrap($input).trigger("change", { force: true });
    });
  });
});

Cypress.Commands.add("createCourse", () => {
  const course_name = "test " + Math.floor(Math.random() * 100000);
  const course_run =
    new Date().getFullYear() + "_" + Math.floor(Math.random() * 10);

  function makeChar(length) {
    let result = "";
    let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  }
  const course_number = makeChar(2) + Math.floor(Math.random() * 1000);

  cy.get(".nav-actions .new-course-button").wait(500).click();
  // fill the form up
  cy.get("#new-course-name").type(course_name);
  cy.get("#new-course-org").type("Abstract");
  cy.get("#new-course-number").type(course_number);
  cy.get("#new-course-run").type(course_run);
  // click to submite the form
  cy.get(".new-course-save").wait(10).click();
});
