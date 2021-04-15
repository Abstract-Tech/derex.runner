describe("Account settings", () => {
  it("Test authenticated user can access the account settings page", function () {
    cy.visit(Cypress.env("LMS_URL"));
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".toggle-user-dropdown").wait(2000).click();

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

    cy.get("#u-field-select-pref-lang").select("English").should("value", "en");
  });
});
