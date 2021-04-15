describe("logout", () => {
  const cms_url = Cypress.env("CMS_URL");

  it("logout", () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".account-username", { timeout: 10000 }).click();
    cy.get(".nav-account-signout .action", { timeout: 10000 }).click({
      force: true,
    });
  });
});
