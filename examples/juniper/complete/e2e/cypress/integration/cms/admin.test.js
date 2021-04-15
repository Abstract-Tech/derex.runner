describe("Knowledge Base Application", () => {
  // previous test omitted for brevity
  it("Should be able to login: admin", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
  });
});
