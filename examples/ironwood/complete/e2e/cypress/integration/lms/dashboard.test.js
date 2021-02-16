describe("Dashboard", () => {
  const lms_url = Cypress.env("LMS_URL");
  // previous test omitted for brevity
  it("test after you login you go to the dashboard", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit(lms_url + "/courses");
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    cy.get("#user-menu .dropdown-item a[href$='/dashboard']")
      .wait(1500)
      .click({ force: true });
  });
});
