describe("LMS tests", () => {
  it("Visit the LMS homepage", () => {
    cy.visit(Cypress.env("LMS_URL"));
    cy.contains("Welcome to TestEdX");
  });
});
