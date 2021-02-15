describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  Cypress.on("uncaught:exception", (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
  });

  it("As a logged in user I should be able to access the courseware of a course i’m enrolled in", function () {
    cy.login(lms_url, Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });
    cy.visit("/courses");
    cy.get(
      ".course[aria-label='Hereditary Gastrointestinal Polyp Syndromes']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".register").then(($button) => {
      cy.wrap($button).click();
    });

    // the course number 14 on the dashbord
    cy.get(
      "#course-card-14 > .details > .wrapper-course-details > .wrapper-course-actions > .course-actions > .course-target-link"
    ).then(($button) => {
      cy.wrap($button).click();
    });
  });
});
