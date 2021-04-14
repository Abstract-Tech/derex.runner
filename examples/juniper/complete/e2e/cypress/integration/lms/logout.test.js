describe("Logout test ", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("User can logout after logged in ", () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));

    cy.visit(lms_url);
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click({ force: true });
    });
    // click the logout button
    cy.get("#user-menu > :nth-child(4) > a").click({ force: true });
  });
});
