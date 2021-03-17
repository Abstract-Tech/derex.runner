describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  it("check for profile ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    cy.get("#user-menu  .dropdown-item a[href$='/u/superuser']").then(($button) => {
      cy.wrap($button).click({ force: true });
    });
    cy.get(".profile-image-field > .u-field").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".clickable > .u-field-value-readonly").type("test");
  });
});