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
  // Open the Stage login page to create session
  cy.request({
    url: `${Cypress.env("login_api_url")}?skip_authn_mfe=true`,
    failOnStatusCode: false,
  });
  // Save csrftoken and use it in header to send Login Post request
  cy.getCookie("csrftoken")
    .its("value")
    .then(($token) => {
      cy.request({
        method: "POST",
        url: `${Cypress.env("login_api_url")}?skip_authn_mfe=true`,
        form: true,
        body: {
          email: email,
          password: password,
          remember: false,
        },
        headers: {
          Referer: Cypress.env("login_url"),
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

Cypress.Commands.add("upload_file", (fileName) => {
  cy.get("#fileupload input[type=file]").then((subject) => {
    cy.fixture(fileName, "base64")
      .then(Cypress.Blob.base64StringToBlob)
      .then((blob) => {
        const el = subject[0];
        const testFile = new File([blob], fileName, {
          type: "application/tar+gzip",
        });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(testFile);
        el.files = dataTransfer.files;
        cy.wrap(subject).trigger("change", { force: true });
      });
  });
});

Cypress.Commands.add("createCourse", () => {
  const course_name = "test " + Math.floor(Math.random() * 100000);
  const course_run = new Date().getFullYear();

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
  cy.get("#new-course-org").type(makeChar(6));
  cy.get("#new-course-number").type(course_number);
  cy.get("#new-course-run").type(course_run);
  // click to submite the form
  cy.get(".new-course-save").wait(10).click();
});

//
class LandingPage {
  getLogoAltAttributes(logoContainer, attributeName, logoType = "/") {
    // This function takes parent container name, logo type and attribute name
    // as parameter and return attribute value
    return cy
      .get(logoContainer)
      .find(`a[href="${logoType}"]>img`)
      .invoke("attr", attributeName);
  }

  getFooterNavItems() {
    return cy.get("footer .nav-item .nav-link");
  }

  getUserEmail() {
    return cy.get("header .navbar #pgn__dropdown-trigger-0").invoke("text");
  }

  enterpriseListContainer() {
    return cy.get(".enterprise-list");
  }

  getEnterpriseList() {
    return cy.get(".enterprise-list td a");
  }

  searchEnterprise(enterpriseName) {
    cy.server();
    cy.route(`**search=${enterpriseName}**`).as("results");
    cy.get('input[name="searchfield-input"]')
      .clear()
      .type(`${enterpriseName}{enter}`);
    cy.wait("@results");
  }

  goToEnterprise(enterpriseName) {
    // Open target enterprise page
    cy.get(".enterprise-list td>a").contains(enterpriseName).click();
    // Wait for page to load properly by verifying that dashboard cards are visible
    cy.get(".card").should("be.visible");
  }

  logoutUser() {
    cy.get("header .navbar .dropdown-toggle")
      .should("have.attr", "aria-expanded", "false")
      .click()
      .should("have.attr", "aria-expanded", "true");
    cy.get("header .navbar .dropdown-item").contains("Logout").click();
  }

  openCodeManagement() {
    cy.get("#sidebar .nav-item:nth-of-type(2) .nav-link")
      .trigger("mouseover")
      .click()
      .trigger("mouseout");
    cy.get(".d-flex.expanded.has-shadow").should("not.be.visible");
  }
}

export default LandingPage;
