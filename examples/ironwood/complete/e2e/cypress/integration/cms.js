describe("CMS tests", () => {
  it("Visit the CMS homepage", () => {
    cy.visit(Cypress.env("CMS_URL"));
    cy.contains("Welcome to Your Platform Studio");
  });
});
