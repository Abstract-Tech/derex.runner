describe("Forget Password", () => {
  it("user can reset the password", () => {
    cy.visit("/");
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.get("#login-email").type(Cypress.env("user_email"));
    cy.get(".forgot-password").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get("#password-reset-email").type("staff@example.com");
    cy.get("#password-reset > .action").then(($button) => {
      cy.wrap($button).click();
    });
  });
});
