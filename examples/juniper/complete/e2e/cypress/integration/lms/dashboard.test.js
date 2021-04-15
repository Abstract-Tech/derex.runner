describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  it("Should be able to login: admin", function () {
    cy.login(lms_url, Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    cy.get("#user-menu .dropdown-item a[href$='/dashboard']")
      .wait(1500)
      .click({ force: true });
    cy.get("#actions-dropdown-link-1 > .fa").then(($button) => {
      cy.wrap($button).click();
    });
    /*  cy.get("#unenroll-1").wait(1000).click();
                            cy.get(".submit-button").wait(1000).click(); */
    cy.get(
      "#course-card-0 > .details > .wrapper-course-details > .wrapper-course-actions > .course-actions > .course-target-link"
    ).then(($button) => {
      cy.wrap($button).click();
    });
  });
});

describe(" this test to let the user go after log in to the dashborad", () => {
  // the url to the lms
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  it("Should be able after the login to go to dashboard", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    // go to courses page
    cy.visit(lms_url + "/courses");
    // use the dropdown button to go to dashboard page
    cy.get(".toggle-user-dropdown").click();
    cy.get("#user-menu .dropdown-item a[href$='/dashboard']")
      .wait(1500)
      .click({ force: true });
  });
});
